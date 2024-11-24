
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


# Create your views here.



def index(request):
    products = Product.objects.filter(is_active=True)
    
    product_data = []
    
    for product in products:
        variants = ProductVariant.objects.filter(Product=product)
        images = ProductImages.objects.filter(Product=product)
        
        product_data.append({
            'product': product,
            'variants': variants,
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
        variants = ProductVariant.objects.filter(Product=product)
        images = ProductImages.objects.filter(Product=product)
        
        product_data.append({
            'product': product,
            'variants': variants,
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
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        return redirect('accounts:manage_addresses')
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

            # Check if the variant is already in the user's wishlist
            wishlist_item = Wishlist.objects.filter(user=user, variant=variant).first()

            if wishlist_item:
                # If the variant is already in the wishlist, remove it
                wishlist_item.delete()
                in_wishlist = False
            else:
                # If the variant is not in the wishlist, add it
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
    
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, "userside/accounts/wishlist.html", {"wishlist_items": wishlist_items})