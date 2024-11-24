from django.db import models
from nutri_auth.models import User
from product.models import Product,ProductVariant





# Cart model for each user's cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    # Total price of all items in the cart
    def get_cart_total(self):
        total = sum(item.sub_total() for item in self.items.all())
        return total


# CartItem model to store each item in the cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.quantity} x {self.variant} in {self.cart}"
    
    def sub_total(self):
        if self.variant.offer_price is not None:
            return self.variant.offer_price * self.quantity
        return 0 
