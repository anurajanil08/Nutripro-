from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    
    path('add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('view/', views.view_cart, name='view_cart'),
    path('update_cart_item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add/', views.add_address, name='add_address'),
]