from django.urls import path
from . import views


app_name = "category"

urlpatterns = [
    path('listcategory/', views.category_list, name='listcategory'),
    path('create-category/', views.create_category, name='create_category'),
    path('editcategory/<int:id>/', views.edit_category, name='edit_category'),
    path('toggle/<int:category_id>/', views.toggle_category_status, name='toggle_status'),
    path('delete/<int:id>/', views.delete_category, name='delete_category'),
]
