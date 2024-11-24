from django.urls import path
from . import views

app_name = "nutri_auth"

urlpatterns = [
  path('signup/',views.signup,name='signup'),
  path('login/',views.handlelogin,name='handlelogin'),
  path('otp/',views.verify_otp,name='verify-otp'),
  path('resent-otp/',views.resend_otp,name='resent-otp'),
  path('logout/', views.logout_view, name='logout'),
  path('forgot-password/', views.forgot_password, name='forgot_password'),
  path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
  
]