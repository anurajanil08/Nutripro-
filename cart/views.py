from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cart, CartItem
from product.models import ProductVariant

@login_required
def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item is already in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    if not created:
        cart_item.quantity += 1  # Increase quantity if already in cart
    cart_item.save()
    return redirect('cart:view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
    }
    return render(request, 'cart/view_cart.html', context)

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()  # Remove item if quantity is set to zero
    return redirect('cart:view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart:view_cart')
