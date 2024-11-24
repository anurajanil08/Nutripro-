from django.contrib import admin
from .models import Coupon

class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'discount_percentage', 
        'max_discount_amount', 
        'minimum_order_amount',
        'expiry_date',
        'is_active',
        'max_usage',
    )
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('name', 'code')

admin.site.register(Coupon, CouponAdmin)

