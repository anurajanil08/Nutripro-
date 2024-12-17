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
            'max_usage',
            'is_active',
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
            'max_usage': 'Maximum Usage',
            'is_active': 'Is Active',
        }

    def clean_discount_percentage(self):
        """Validate the discount percentage."""
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if not (0 < discount_percentage <= 100):
            raise ValidationError("Discount percentage must be greater than 0 and less than or equal to 100.")
        return discount_percentage

    def clean_expiry_date(self):
        """Ensure the expiry date is not in the past."""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date <= timezone.now():
            raise ValidationError("Expiry date cannot be in the past.")
        return expiry_date

    def clean_minimum_order_amount(self):
        """Ensure the minimum order amount is positive."""
        minimum_order_amount = self.cleaned_data.get('minimum_order_amount')
        if minimum_order_amount <= 0:
            raise ValidationError("Minimum order amount must be greater than 0.")
        return minimum_order_amount

    def clean_max_discount_amount(self):
        """Ensure max discount amount is positive."""
        max_discount_amount = self.cleaned_data.get('max_discount_amount')
        if max_discount_amount <= 0:
            raise ValidationError("Maximum discount amount must be greater than 0.")
        return max_discount_amount

    def clean(self):
        """General clean for custom validations."""
        cleaned_data = super().clean()
        discount_percentage = cleaned_data.get('discount_percentage')
        max_discount_amount = cleaned_data.get('max_discount_amount')
        minimum_order_amount = cleaned_data.get('minimum_order_amount')

        # Ensure max discount amount does not exceed possible discount
        if discount_percentage and max_discount_amount:
            max_allowed_discount = (discount_percentage / 100) * minimum_order_amount
            if max_discount_amount > max_allowed_discount:
                raise ValidationError(
                    "Maximum discount amount cannot exceed the calculated allowable discount based on the percentage."
                )

        return cleaned_data


class CouponUsageForm(forms.ModelForm):
    class Meta:
        model = CouponUsage
        fields = ['user', 'coupon', 'times_used']

    def clean_times_used(self):
        """Ensure that the coupon usage count doesn't exceed the max usage."""
        times_used = self.cleaned_data.get('times_used')
        coupon = self.cleaned_data.get('coupon')

        if coupon:
            remaining_uses = coupon.max_usage - coupon.usage_count
            if times_used > remaining_uses:
                raise ValidationError(
                    f"Coupon can only be used {remaining_uses} more times. Current usage exceeds the limit."
                )
        
        return times_used

    def clean(self):
        """General clean for custom validations."""
        cleaned_data = super().clean()
        coupon = cleaned_data.get('coupon')
        user = cleaned_data.get('user')

        if coupon and user:
            # Check if the user has already exceeded usage for this coupon
            coupon_usage = CouponUsage.objects.filter(user=user, coupon=coupon).first()
            if coupon_usage and coupon_usage.times_used >= coupon.max_usage:
                raise ValidationError(
                    f"This user has already used the coupon {coupon.max_usage} times."
                )

        return cleaned_data

