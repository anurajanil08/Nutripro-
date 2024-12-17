from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    
    path('add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('view/', views.view_cart, name='view_cart'),
    path('update-cart-ajax/', views.update_cart_ajax, name='update_cart_ajax'),
    path('get-cart-summary/', views.get_cart_summary, name='get_cart_summary'),
    path('add-to-cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),  
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add/', views.add_address, name='add_address'),


]