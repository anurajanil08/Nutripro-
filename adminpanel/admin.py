from django.contrib import admin
from django.db.models import Sum, Count, F
from order.models import Order, OrderItem
from product.models import Product, ProductVariant


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'final_amount', 'order_status', 'date', 'payment_status')
    list_filter = ('order_status', 'payment_status', 'date')
    search_fields = ('order_id', 'user__username')

    def changelist_view(self, request, extra_context=None):
        """
        Add sales report to the admin changelist view in the adminpanel app.
        """
        queryset = self.get_queryset(request)

        # Calculate total revenue from delivered orders
        total_revenue = queryset.filter(order_status='Delivered').aggregate(
            revenue=Sum('final_amount')
        )['revenue'] or 0

        # Total orders and pending payments
        total_orders = queryset.count()
        pending_payments = queryset.filter(payment_status=False).count()

        # Top-selling products
        best_selling_products = (
            OrderItem.objects.values(product_name=F('variant__Product__Product_name'))
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:5]
        )

        # Add extra context for the sales report
        extra_context = extra_context or {}
        extra_context['sales_report'] = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_payments': pending_payments,
            'best_selling_products': best_selling_products,
        }
        return super().changelist_view(request, extra_context=extra_context)
