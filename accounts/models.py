from django.db import models
from django.conf import settings
from nutri_auth.models import User
from django.db import models  
from product.models import ProductVariant


# Create your models here.
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=50)
    house_name = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100)
    pin_number = models.CharField(max_length=6)  
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default="India")
    phone_number = models.CharField(max_length=15)  

   
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}, {self.house_name}, {self.street_name}, {self.district}, {self.state}, {self.country}"

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username}'s wishlist: {self.variant}"

    