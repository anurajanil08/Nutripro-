from django.db import models

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