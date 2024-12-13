from django.urls import path
from . import views

app_name = 'order'  

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('admin-order-list/', views.admin_order_list, name='admin_order_list'),  
    path('update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin-order-details/<int:order_id>/',views.adorder_details,name='adorder_details'),
    path('my-order/', views.order_list, name='order_list'),
    path('order/cancel/<int:order_id>/',views.cancel_order, name='cancel_order'), 
    path('payment/success/', views.payment_success, name='payment_success'),
    path('order/<int:id>/', views.order_details, name='order_detail'),
    path('download_invoice/<str:order_id>/', views.download_invoice, name='download_invoice'),
    path('returns/', views.manage_returns, name='admin_manage_returns'),
    path('returns/update/<int:return_id>/', views.update_return_status, name='admin_update_return'),
    path('request-return/<str:order_id>/', views.request_return, name='request_return'),

   
]
