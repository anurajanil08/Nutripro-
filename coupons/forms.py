from django import forms
from .models import Coupon, CouponUsage

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'name',
            'code',
            'discount_percentage',  # Updated field
            'minimum_order_amount',
            'max_discount_amount',  # New field
            'expiry_date',
            'is_active',
            'max_usage',
        ]
        widgets = {
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(),
        }
        labels = {
            'name': 'Coupon Name',
            'code': 'Coupon Code',
            'discount_percentage': 'Discount Percentage (%)',  # Updated label
            'minimum_order_amount': 'Minimum Order Amount',
            'max_discount_amount': 'Maximum Discount Amount',  # New label
            'expiry_date': 'Expiry Date',
            'is_active': 'Is Active',
            'max_usage': 'Maximum Usage',
        }
        
class CouponUsageForm(forms.ModelForm):
    class Meta:
        model = CouponUsage
        fields = ['user', 'coupon', 'times_used']

