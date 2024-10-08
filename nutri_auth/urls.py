from django.urls import path
from . import views

urlpatterns = [
  path('signup/',views.signup,name='signup'),
  path('login/',views.handlelogin,name='handlelogin'),
  path('verify_otp/',views.verify_otp,name='verify_otp'),
  path('logout/',views.handlelogout,name='handlelogout'),
  path('otp/', views.otp, name='otp'),  
]