from django.urls import path
from . import views

app_name = 'order'  

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('admin-order-list/', views.admin_order_list, name='admin_order_list'),  
    path('order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin-order-details/<int:order_id>/',views.adorder_details,name='adorder_details'),
    path('my-order/', views.order_list, name='order_list'),
    path('order/cancel/<int:order_id>/',views.cancel_order, name='cancel_order'), 
    path('payment/success/', views.payment_success, name='payment_success'),
    

    # path('order/<int:order_id>/', views.order_details, name='order_details'),  

   
]
