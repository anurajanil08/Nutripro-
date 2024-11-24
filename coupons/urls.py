from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    path('', views.admin_coupon_list, name='coupon_list'),
    path('create/', views.admin_create_coupon, name='create_coupon'), 
    path('edit/<int:id>/', views.admin_create_coupon, name='edit_coupon'),
    path('coupons/<int:id>', views.admin_toggle_coupon_status, name='toggle_coupon_status'),
    path('generate-code/', views.admin_generate_coupon_code, name='admin_generate_coupon_code'),
    path('apply/', views.apply_coupon, name='apply_coupon'),
    path('list/', views.list_active_coupons, name='list_active_coupons'),
]