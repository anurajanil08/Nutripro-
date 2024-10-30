from django import forms
from .models import Product, ProductVariant


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['Product_name', 'Product_description', 'Product_category', 'Product_brand', 'price', 'offer_price', 'is_active']




class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'stock', 'variant_status']  

        widgets = {
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'variant_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }