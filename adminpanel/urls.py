from django.urls import path
from . import views


app_name = "adminpanel"

urlpatterns = [
    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    path("dashboard/", views.dashboard, name="dashboard"), 
    # path("demo/", views.demo, name="demo"),
    path("userlist/",views.list_users,name="userlist"),
    path('toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path("logout/",views.custom_logout_view , name='logout'),
    path('sales/', views.sales_report, name='sales'),

]