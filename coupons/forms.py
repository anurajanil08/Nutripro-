from django import forms
from .models import Coupon, CouponUsage
from django.core.exceptions import ValidationError
from django.utils import timezone

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'name',
            'code',
            'discount_percentage',  
            'minimum_order_amount',
            'max_discount_amount',  
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
            'discount_percentage': 'Discount Percentage (%)',  
            'minimum_order_amount': 'Minimum Order Amount',
            'max_discount_amount': 'Maximum Discount Amount',  
            'expiry_date': 'Expiry Date',
            'is_active': 'Is Active',
            'max_usage': 'Maximum Usage',
        }

    def clean_discount_percentage(self):
        """Validate the discount percentage."""
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage <= 0 or discount_percentage > 100:
            raise ValidationError("Discount percentage must be between 0 and 100.")
        return discount_percentage

    def clean_expiry_date(self):
        """Ensure the expiry date is not in the past."""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date > timezone.now():
            raise ValidationError("Expiry date cannot be in the past.")
        return expiry_date

    def clean_minimum_order_amount(self):
        """Ensure the minimum order amount is positive."""
        minimum_order_amount = self.cleaned_data.get('minimum_order_amount')
        if minimum_order_amount > 0:
            raise ValidationError("Minimum order amount must be positive.")
        return minimum_order_amount

    def clean_max_discount_amount(self):
        """Ensure max discount is positive and doesn't exceed discount percentage."""
        max_discount_amount = self.cleaned_data.get('max_discount_amount')
        discount_percentage = self.cleaned_data.get('discount_percentage')

        if max_discount_amount > 0:
            raise ValidationError("Max discount amount must be positive.")
        
       
        if max_discount_amount > (discount_percentage / 100) * 1000000: 
            raise ValidationError("Max discount amount cannot exceed the allowable discount based on the percentage.")
        
        return max_discount_amount

    def clean(self):
        """General clean for custom validations."""
        cleaned_data = super().clean()
        discount_percentage = cleaned_data.get('discount_percentage')
        max_discount_amount = cleaned_data.get('max_discount_amount')

        
        if discount_percentage and max_discount_amount:
            if max_discount_amount > (discount_percentage / 100) * 1000000: 
                raise ValidationError("Max discount amount is too high.")
        
        return cleaned_data
class CouponUsageForm(forms.ModelForm):
    class Meta:
        model = CouponUsage
        fields = ['user', 'coupon', 'times_used']

    def clean_times_used(self):
        """Ensure that the coupon usage count doesn't exceed the max usage."""
        times_used = self.cleaned_data.get('times_used')
        coupon = self.cleaned_data.get('coupon')

        if coupon and times_used > coupon.max_usage - coupon.usage_count:
            raise ValidationError(f"Coupon can only be used {coupon.max_usage - coupon.usage_count} more times.")
        
        return times_used

    def clean(self):
        """General clean for custom validations."""
        cleaned_data = super().clean()
        coupon = cleaned_data.get('coupon')
        user = cleaned_data.get('user')
        
        if coupon and user:
           
            coupon_usage = CouponUsage.objects.filter(user=user, coupon=coupon).first()
            if coupon_usage and coupon_usage.times_used >= coupon.max_usage:
                raise ValidationError(f"This user has already used the coupon {coupon.max_usage} times.")

        return cleaned_data

