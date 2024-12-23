
from product.models import Product,ProductVariant,ProductImages
from django.shortcuts import render
from category.models import Category
from brand.models import Brand
from django.db.models import Count, Avg
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import UserAddress
from .forms import UserAddressForm
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Wishlist
import json
from django.contrib import messages
from cart.models import Cart, CartItem
from order.models import Order


# Create your views here.



























def index(request):
    products = Product.objects.filter(is_active=True)
    
    product_data = []
    
    for product in products:
        first_variant = ProductVariant.objects.filter(Product=product).first()
        images = ProductImages.objects.filter(Product=product)
        
        product_data.append({
            'product': product,
            'first_variant': first_variant,
            'images': images
        })
    
    context = {
        'product_data': product_data,
    }

    return render(request, "userside/index.html", context)

def shop_page(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    product_data = []
    
    for product in products:
        variant = ProductVariant.objects.filter(Product=product).first() 
        images = ProductImages.objects.filter(Product=product)
        
        product_data.append({
            'product': product,
            'variant': variant,
            'images': images
        })
    
    context = {
        'product_data': product_data,
        'categories': categories,
        'brands': brands,
    }

    return render(request, "userside/store.html", context)


def shop_ajax(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        category_names = request.GET.getlist('category')
        brand_names = request.GET.getlist('brand')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort_by = request.GET.get('sort_by', 'created_at')
        search_query = request.GET.get('search', '')

        products = Product.objects.filter(is_active=True)

        
        if search_query:
            products = products.filter(Product_name__icontains=search_query)


        
        if category_names:
            products = products.filter(Product_category__category_name__in=category_names)

        
        if brand_names:
            products = products.filter(Product_brand__brand_name__in=brand_names)

        
        try:
            if min_price:
                products = products.filter(price__gte=float(min_price))
            if max_price:
                products = products.filter(price__lte=float(max_price))
        except ValueError:
            return JsonResponse({'error': 'Invalid price range'}, status=400)

        
        if sort_by == 'popularity':
            products = products.annotate(num_orders=Count('cartitem')).order_by('-num_orders')
        elif sort_by == 'price_low_high':
            products = products.order_by('offer_price')
        elif sort_by == 'price_high_low':
            products = products.order_by('-offer_price')
        elif sort_by == 'average_ratings':
            products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort_by in ['featured', 'new_arrivals']:
            products = products.order_by('-created_at')
        elif sort_by == 'a_to_z':
            products = products.order_by('name')
        elif sort_by == 'z_to_a':
            products = products.order_by('-name')

        
        product_data = []
        for product in products:
            variants = ProductVariant.objects.filter(Product=product)
            images = ProductImages.objects.filter(Product=product)
            product_data.append({
                'product': product,
                'variants': variants,
                'images': images,
            })

        html = render_to_string('userside/product_grid.html', {'product_data': product_data})
        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Invalid request'}, status=400)



def about(request):
  return render(request,"about.html")

@login_required
def account_dashboard(request):
    
    context = {
        'user': request.user,
        
    }
    return render(request, 'userside/accounts/dash.html')


@login_required
def manage_addresses(request):
    addresses = UserAddress.objects.filter(user=request.user)
    form = UserAddressForm(request.POST or None)
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        if address_id:
            address = get_object_or_404(UserAddress, id=address_id, user=request.user)
            form = UserAddressForm(request.POST, instance=address)
        else:
            form = UserAddressForm(request.POST)
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('accounts:manage_addresses')
    
    return render(request, 'userside/accounts/manage_addresses.html', {'form': form, 'addresses': addresses})


@login_required
def delete_address(request, pk):
    print("hi")
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('accounts:manage_addresses')
    return render(request, 'userside/accounts/delete_address.html', {'address': address})

@login_required
def add_address(request):
    form = UserAddressForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request,"Address added successfully!")
            return redirect('accounts:manage_addresses')
        else:
            messages.error(request,"Address added sucessfully!")    
    return render(request, 'userside/accounts/add_edit_address.html', {'form': form})

@login_required
def edit_address(request, id):
    address = get_object_or_404(UserAddress, id=id, user=request.user)
    form = UserAddressForm(request.POST or None, instance=address)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('accounts:manage_addresses')
    return render(request, 'userside/accounts/add_edit_address.html', {'form': form, 'address': address})



#wishlist
def toggle_wishlist(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        variant_id = request.POST.get('variant_id')
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            user = request.user

            
            wishlist_item = Wishlist.objects.filter(user=user, variant=variant).first()

            if wishlist_item:
                
                wishlist_item.delete()
                in_wishlist = False
            else:
                
                Wishlist.objects.create(user=user, variant=variant)
                in_wishlist = True

            return JsonResponse({
                'message': 'Wishlist updated successfully',
                'is_in_wishlist': in_wishlist
            })
        except ProductVariant.DoesNotExist:
            return JsonResponse({'error': 'Variant not found'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)




@login_required
def view_wishlist(request):
    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related('variant__Product')  
    )
    return render(request, "userside/accounts/wishlist.html", {"wishlist_items": wishlist_items})




#remove
@login_required
def remove_from_wishlist(request, variant_id):
    if request.method == "POST":
        variant = get_object_or_404(ProductVariant, id=variant_id)
        wishlist_item = Wishlist.objects.filter(user=request.user, variant=variant).first()
        
        if wishlist_item:
            wishlist_item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed from wishlist'})
        else:
            return JsonResponse({'success': False, 'message': 'Item not found in your wishlist'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)







def get_counts(request):
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user).first()
        cart_count = CartItem.objects.filter(cart=cart).count() if cart else 0
    else:
        wishlist_count = 0
        cart_count = 0

    return JsonResponse({
        'wishlist_count': 2,
        'cart_count': 5,
    })



def get_dashboard_stats(request):
    if request.user.is_authenticated:
        total_orders = Order.objects.filter(user=request.user).count()
        wishlist_items = Wishlist.objects.filter(user=request.user).count()
        saved_addresses = UserAddress.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart).count() if cart else 0
    else:
        total_orders = 0
        wishlist_items = 0
        saved_addresses = 0
        cart_items = 0

    stats = {
        'total_orders': total_orders,
        'wishlist_items': wishlist_items,
        'saved_addresses': saved_addresses,
        'cart_items': cart_items,
    }
    return JsonResponse(stats)