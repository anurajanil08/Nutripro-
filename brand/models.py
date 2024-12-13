from django.db import models
from django.db.models import Count


# Create your models here.
class Brand(models.Model):
    brand_name = models.CharField(max_length=40, null=False, unique=True)
    description = models.TextField(max_length=255, blank=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.brand_name = self.brand_name.capitalize()
        super(Brand, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.brand_name
    

    @staticmethod
    def get_top_10_brands():
        from order.models import OrderItem 
        return (
            Brand.objects.filter(
                product__productvariant__orderitem__order__order_status="Delivered"
            )
            .annotate(total_sales=Count('product__productvariant__orderitem'))
            .order_by('-total_sales')[:10]
        )