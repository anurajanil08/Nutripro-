from django.urls import path
from . import views

app_name = "product"


urlpatterns = [
    path('list-product/', views.product_list, name='list-product'),
    path('addproduct/', views.add_product, name='addproduct'),
    path('add-images/<int:product_id>/', views.add_images, name='add-images'),
    path('product/<int:product_id>/edit_images/', views.edit_images, name='edit_images'),
    path('product_detail/<int:product_id>',views.product_detail,name='product-detail'),
    path('edit/<int:product_id>/', views.edit_product, name='product_edit'),
    path('image/delete/<int:image_id>/', views.delete_image, name='delete_image'),
    path('product-status/<int:pk>/', views.toggle_product_status, name='product_status'),
    path('product/variant/<int:product_id>/', views.product_variant, name='product_variant'),
    path('add_variant/<int:product_id>', views.add_variant, name='add_variant'),
    path('variant/<int:variant_id> ', views.edit_variant, name='edit_variant'),
    path('variant-status/<int:variant_id>/', views.toggle_variant_status, name='variant_status'),
    path('product_detail_page/<int:product_id>',views.product_detail_page,name='product-detail-page'),
    path('product/delete-review/<int:review_id>/', views.delete_review, name='delete-review'),
    


]