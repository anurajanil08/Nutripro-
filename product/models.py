from django.db import models
from category.models import Category
from brand.models import Brand
from nutri_auth.models import User
from django.db.models import Count


# Create your models here.


class Product(models.Model):
    Product_name = models.CharField(max_length=100, null=False)
    Product_description = models.TextField(max_length=5000, null=False)
    Product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    Product_brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    thumbnail = models.ImageField(upload_to="Product_thumbnails", null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.Product_name
    
    @staticmethod
    def get_top_10_best_selling_products():
        from order.models import OrderItem  # Import here to avoid circular imports

        return (
            Product.objects.filter(
                productvariant__orderitem__order__order_status="Delivered"
            )
            .annotate(total_sales=Count('productvariant__orderitem'))
            .order_by('-total_sales')[:10]
        )

class ProductVariant(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, null=True)
    stock = models.BigIntegerField(null=False, default=0)
    variant_status = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  

    def percentage_discount(self):
        return int(((self.price - self.offer_price) / self.price) * 100)
    

    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return f"{self.Product.Product_name} - {self.size}"
    


class ProductImages(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    images = models.ImageField(upload_to="Product_images")

    def __str__(self):
        return f"Image for {self.Product.Product_name}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.IntegerField()
    comment = models.TextField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.Product.Product_name}"
