from django.urls import path
from . import views

app_name = 'wallet' 

urlpatterns = [
    path('user-wallet/', views.wallet_detail, name='wallet_detail'),
    
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),
]
