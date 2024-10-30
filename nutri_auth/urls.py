from django.urls import path
from . import views

app_name = "nutri_auth"

urlpatterns = [
  path('signup/',views.signup,name='signup'),
  path('login/',views.handlelogin,name='handlelogin'),
  path('otp/',views.verify_otp,name='verify-otp'),
  path('resent-otp/',views.resend_otp,name='resent-otp'),
  path('logout/', views.logout_view, name='logout'),
  
]