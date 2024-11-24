from django import forms
from .models import Product, ProductVariant, Category, Brand

class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        required=False, 
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(), 
        required=False, 
        label="Brand",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False, 
        min_value=0, 
        label="Min Price",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_price = forms.DecimalField(
        required=False, 
        min_value=0, 
        label="Max Price",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False, 
        label="Only Active Products",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    size = forms.CharField(
        max_length=10, 
        required=False, 
        label="Size",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
