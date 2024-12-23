from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("shoppage/", views.shop_page, name="shop_page"),
    path('shop/', views.shop_ajax, name='shop-ajax'),
    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('addresses/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('my-account/', views.account_dashboard, name='dash'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:id>/', views.edit_address, name='edit_address'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('view/', views.view_wishlist, name='wishlist'),
    path('wishlist/remove/<int:variant_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('get-counts/', views.get_counts, name='get_counts'),
    path('api/dashboard-stats/', views.get_dashboard_stats, name='dashboard_stats'),


]