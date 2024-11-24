from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import  now
from django.utils import timezone

User = get_user_model()

class Coupon(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2) 
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_usage = models.IntegerField(default=1)
    usage_count = models.IntegerField(default=0)

    def is_valid(self):
        """Check if the coupon is valid"""
        if not self.is_active:
            return False
        if self.expiry_date < timezone.now():
            return False
        if self.usage_count >= self.max_usage:
            return False
        return True

    def __str__(self):
        return f"{self.code} - Discount: ₹{self.discount_percentage}"

  
class CouponUsage(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupon_usages")  
  coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")  
  times_used = models.IntegerField(default=0) 

  def __str__(self):
      return f"{self.user.username} - {self.coupon.code} - Used: {self.times_used} times" 
  