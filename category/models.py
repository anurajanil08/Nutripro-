from django.db import models




class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True) 
    category_description = models.TextField(blank=True, null=True) 
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return self.category_name
