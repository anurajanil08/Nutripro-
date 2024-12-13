from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'category_description', 'is_active', 'offer_percentage']
        widgets = {
            'category_description': forms.Textarea(attrs={
                'rows': 4, 
                'cols': 40, 
                'placeholder': 'Enter category description here...',
                'class': 'form-control',
            }),
            'offer_percentage': forms.NumberInput(attrs={
                'min': 0, 
                'max': 100, 
                'placeholder': 'Enter a discount percentage',
                'class': 'form-control',
            }),
        }
        labels = {
            'category_name': 'Category Name',
            'category_description': 'Description',
            'is_active': 'Active',
            'offer_percentage': 'Offer Percentage',
        }
        help_texts = {
            'offer_percentage': 'Enter a percentage discount for this category.',
        }
