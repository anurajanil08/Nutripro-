from cart.models import Cart, CartItem
from order.models import Order
from .models import Wishlist, UserAddress
from django.http import JsonResponse

def dashboard_stats(request):
    if request.user.is_authenticated:
        total_orders = Order.objects.filter(user=request.user).count()
        wishlist_items = Wishlist.objects.filter(user=request.user).count()
        saved_addresses = UserAddress.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user).first() 
        if cart:
            cart_items = CartItem.objects.filter(cart=cart).count()
        else:
            cart_items = 0
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
    return {'dashboard_stats': stats}





