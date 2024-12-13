from django.db import models
from django.db.models import Count





class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True) 
    category_description = models.TextField(blank=True, null=True) 
    is_active = models.BooleanField(default=True) 
    offer_percentage = models.PositiveIntegerField(
        default=0, 
        help_text="Percentage discount for this category."
    )
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return self.category_name
    

    @staticmethod
    def get_top_10_categories():
        from order.models import OrderItem  

        return (
            Category.objects.filter(
                product__productvariant__orderitem__order__order_status="Delivered"
            )
            .annotate(total_sales=Count('product__productvariant__orderitem'))
            .order_by('-total_sales')[:10]
        )
    

