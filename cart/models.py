from django.db import models
from nutri_auth.models import User
from product.models import Product,ProductVariant






class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    #
    def get_cart_total(self):
        total = sum(item.sub_total() for item in self.items.all())
        return total



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
            base_sub_total = self.variant.offer_price * self.quantity

            category_offer = self.product.Product_category.offer_percentage if self.product.Product_category else 0
            
            if category_offer > 0:
                discount = (base_sub_total * category_offer) / 100
                return base_sub_total - discount

            return base_sub_total
        
        return 0
    

    def discounted_price(self):
        price = self.variant.offer_price if self.variant.offer_price is not None else 0
        category_offer = self.product.Product_category.offer_percentage if self.product.Product_category else 0

        if category_offer > 0:
            discount = (price * category_offer) / 100
            return price - discount

        return price
