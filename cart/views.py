from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem
from product.models import ProductVariant
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
import json
from accounts.forms import UserAddressForm
from django.utils import timezone
from django.db.models import F
from coupons.models import Coupon, CouponUsage
from django.db.models import F, Q
from django.utils import timezone
from order.models import Order
from django.utils.timezone import now
from order.models import Order, OrderAddress
from django.utils.crypto import get_random_string
from nutri_auth.models import User
from django.utils.timezone import now
from django.db.models import Q, F

@login_required
def add_to_cart(request, variant_id):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        product = variant.Product  
        stock = variant.stock  
        quantity = int(request.POST.get('quantity', 1))  

        
        if quantity < 1 or quantity > MAX_QUANTITY:
            return JsonResponse({'success': False, 'message': f'Quantity must be between 1 and {MAX_QUANTITY}.'})

        
        if quantity > stock:
            return JsonResponse({'success': False, 'message': 'Insufficient stock available.'})

        
        cart, created = Cart.objects.get_or_create(user=request.user)

        
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': 0}  
        )

        
        total_quantity = cart_item.quantity + quantity

        
        if total_quantity > MAX_QUANTITY:
            return JsonResponse({'success': False, 'message': f'Cannot add more than {MAX_QUANTITY} items of this product.'})

        
        cart_item.quantity = total_quantity
        cart_item.save()

        return JsonResponse({'success': True, 'message': 'Item added to cart.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)



from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
import json

# Constants
MAX_QUANTITY = 5

@login_required
def view_cart(request):
    """
    Render the cart page with initial cart items.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant')
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(float(item.sub_total()) for item in cart_items)

    return render(request, 'userside/cart/view_cart.html', {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
    })


@login_required
@require_POST
def update_cart_ajax(request):
    """
    AJAX endpoint to dynamically update cart item quantity.
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        action = data.get('action', 'update')

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if action == 'update':
            new_quantity = int(data.get('quantity', 1))

            # Validate and update quantity
            valid, message = validate_quantity(item, new_quantity)
            print(valid)
            if not valid:
                print("not valit")
                return JsonResponse({'success': False, 'message': message})

            item.quantity = new_quantity
            item.save()

            return JsonResponse({
                'success': True,
                'action': 'update',
                'item_id': item.id,
                'quantity': item.quantity,
                'subtotal': float(item.sub_total()),
                'total_price': calculate_total_price(request.user)
            })

        elif action == 'remove':
            item.delete()

            return JsonResponse({
                'success': True,
                'action': 'remove',
                'item_id': item_id,
                'total_price': calculate_total_price(request.user)
            })

        return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def validate_quantity(item, quantity):
    """
    Validate the quantity for a cart item.
    Returns a tuple (is_valid, message).
    """
    # Remove the item if quantity is less than 1
    if quantity < 1:
        item.delete()
        return False, 'Item removed from cart.'

    # Check stock availability
    if quantity > item.variant.stock:
        return False, f'Only {item.variant.stock} units available.'

    # Set a maximum quantity limit
    MAX_QUANTITY = 5  
    if quantity > MAX_QUANTITY:
        return False, f'Maximum quantity is {MAX_QUANTITY}.'

    return True, ''


def calculate_total_price(user):
    """
    Calculate total price for a user's cart.
    """
    try:
        cart = Cart.objects.get(user=user)
        return sum(
            float(item.sub_total())
            for item in cart.items.select_related('variant', 'product')
        )
    except Cart.DoesNotExist:
        return 0.0


@login_required
def get_cart_summary(request):
    """
    AJAX endpoint to get current cart summary.
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'variant')

        items_data = []
        for item in cart_items:
            items_data.append({
                'id': item.id,
                'product_name': item.product.Product_name,
                'variant': item.variant.size,
                'quantity': item.quantity,
                'price': float(item.variant.offer_price) if item.variant.offer_price else 0.0,
                'subtotal': float(item.sub_total()),
                'thumbnail': item.product.thumbnail.url if item.product.thumbnail else None
            })

        return JsonResponse({
            'success': True,
            'items': items_data,
            'total_price': calculate_total_price(request.user)
        })
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cart not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)










        


































def checkout(request):
    
    user_cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=user_cart, is_active=True) if user_cart else []


    if not user_cart or not cart_items:
        messages.error(request, "Your cart is empty.")
        print('Cart is empty or inactive items.')
        return redirect('cart:view_cart')

    critical_error = False

    for item in cart_items:
        print(f"Checking item: {item}")
        if not item.product.is_active:
            messages.error(request, f"{item.product.Product_name} is currently unavailable.")
            critical_error = True
        elif not item.variant.variant_status:
            messages.error(request, f"{item.variant.Product.Product_name} ({item.variant.size}g) is currently unavailable.")
            critical_error = True
        elif item.variant.stock < item.quantity:
            messages.error(request, f"{item.variant.Product.Product_name} ({item.variant.size}g) does not have enough stock.")
            critical_error = True

    if critical_error:
        return redirect('cart:view_cart')

    total_price = sum(item.sub_total() for item in cart_items)

    addresses = request.user.addresses.all()


    valid_coupons = Coupon.objects.filter(
        is_active=True,
        expiry_date__gte=now()
    ).exclude(
        Q(usages__user=request.user) & Q(usages__times_used__gte=F('max_usage'))
    ).distinct()


    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'addresses': addresses,
        'coupons': valid_coupons,
    }

    return render(request, 'userside/cart/checkout.html', context)




def add_address(request):
    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        if form.is_valid():
            
            new_address = form.save(commit=False)
            new_address.user = request.user  
            new_address.save()

            messages.success(request, "Address added successfully.")
            return redirect('cart:checkout')  

        else:
            messages.error(request, "There was an error adding the address.")
    else:
        form = UserAddressForm()

    return render(request, 'userside/cart/add_address.html', {'form': form})