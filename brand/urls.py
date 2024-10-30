
from django.urls import path
from . import views

app_name = "brand"
urlpatterns = [
    path('create/', views.create_brand, name='createbrand'),
    path('edit/<int:pk>/', views.edit_brand, name='editbrand'),
    path('brandlist/', views.brand_list, name='brandlist'),
    path('toggle/<int:id>/', views.toggle_brand, name='toggle_brand'),
    path('delete/<int:brand_id>/', views.delete_brand, name='deletebrand'),
]
