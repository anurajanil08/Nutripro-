# Create your models here.
from django.db import models
from nutri_auth.models import User 
from product.models import ProductVariant  
from decimal import Decimal


class OrderAddress(models.Model):
    name = models.CharField(max_length=50)
    house_name = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100)
    pin_number = models.IntegerField()
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.street_name}, {self.district}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Awaiting Payment', 'Awaiting Payment'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
        ('Returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='Pending')
    payment_option = models.CharField(max_length=50, default="Cash on Delivery")
    order_id = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.final_amount = self.total_amount - self.discount_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, blank=True, null=True)

    def total_cost(self):
        return Decimal(self.quantity) * self.price

    def __str__(self):
        return f"{self.variant.Product.Product_name} x {self.quantity} (Order #{self.order.order_id})"
