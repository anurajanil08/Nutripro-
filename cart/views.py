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



@login_required
def add_to_cart(request, variant_id):
    print("add_to_cart view accessed") 
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        product = variant.Product 
        quantity = int(request.POST.get('quantity', 1))
        print(f"Variant ID: {variant_id}, Quantity: {quantity}")  

        
        cart, created = Cart.objects.get_or_create(user=request.user)

        
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,  
            variant=variant,
            defaults={'quantity': quantity}
        )

      
        if not item_created:
            if cart_item.quantity + quantity > MAX_QUANTITY:
                return JsonResponse({'success': False, 'message': f'Cannot add more than {MAX_QUANTITY} items of this product.'})
            cart_item.quantity += quantity
            cart_item.save()
        elif quantity > MAX_QUANTITY:
            return JsonResponse({'success': False, 'message': f'Cannot add more than {MAX_QUANTITY} items of this product.'})

        print(f"Cart item added: {cart_item}") 

        return JsonResponse({'success': True, 'message': 'Item added to cart'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


MAX_QUANTITY = 5

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'variant') 
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.sub_total() for item in cart_items)

    return render(request, 'userside/cart/view_cart.html', {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
    })


@require_POST
def update_cart_item(request, item_id):
    """Update the quantity of a specific cart item"""
    try:
        item = get_object_or_404(CartItem, id=item_id)
        data = json.loads(request.body)
        new_quantity = data.get('quantity', 1)

        if new_quantity > MAX_QUANTITY:
            return JsonResponse({'success': False, 'message': f'Quantity cannot exceed {MAX_QUANTITY}.'})
        elif new_quantity < 1:
            item.delete()
            return JsonResponse({'success': True, 'deleted': True, 'total_price': calculate_total_price()})
        
        item.quantity = new_quantity
        item.save()

        return JsonResponse({
            'success': True,
            'subtotal': item.sub_total,  
            'total_price': calculate_total_price()  
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def remove_from_cart(request, item_id):
    """Remove a specific item from the cart."""
    if request.method == 'POST':
        try:
            
            item = get_object_or_404(CartItem, id=item_id)
            item.delete()

            
            total_price = calculate_total_price(request.user.cart) if hasattr(request.user, 'cart') else 0

            return JsonResponse({
                'success': True,
                'total_price': total_price
            })
        except Exception as e:
            
            print(f"Error removing item from cart: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred while removing the item.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def calculate_total_price():
    """Helper function to calculate total cart price"""
    
    return CartItem.objects.aggregate(total=models.Sum('sub_total'))['total'] or 0


def checkout(request):
    user_cart = Cart.objects.filter(user=request.user).first()
    if not user_cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view_cart')

    cart_items = CartItem.objects.filter(cart=user_cart, is_active=True)
    invalid_items = []

    for item in cart_items:
        if not item.variant.variant_status or item.variant.stock < item.quantity:
            invalid_items.append(item)

    # Handle invalid items
    if invalid_items:
        for item in invalid_items:
            messages.error(
                request,
                f"Item {item.variant.Product.Product_name} ({item.variant.size}) is not available or has insufficient stock."
            )
        return redirect('cart:view_cart')

    # Calculate total price using the Cart model's method
    total_price = user_cart.get_cart_total()

    addresses = request.user.addresses.all()

    valid_coupons = Coupon.objects.filter(
    is_active=True,
    expiry_date__gte=timezone.now()
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