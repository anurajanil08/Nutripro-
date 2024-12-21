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

    # Field-specific validation for category_name
    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if not category_name:
            raise forms.ValidationError("Category name is required.")
        if len(category_name) < 3:
            raise forms.ValidationError("Category name must be at least 3 characters long.")
        if not category_name.isalpha():
            raise forms.ValidationError("Category name must contain only alphabets.")
        return category_name

    # Field-specific validation for offer_percentage
    def clean_offer_percentage(self):
        offer_percentage = self.cleaned_data.get('offer_percentage')
        if offer_percentage is None:
            raise forms.ValidationError("Offer percentage is required.")
        if offer_percentage < 0 or offer_percentage > 90:
            raise forms.ValidationError("Offer percentage must be between 0 and 90.")
        return offer_percentage

    # Cross-field validation
    def clean(self):
        cleaned_data = super().clean()
        category_name = cleaned_data.get('category_name')
        category_description = cleaned_data.get('category_description')

        if category_name and category_description:
            if category_name.lower() in category_description.lower():
                raise forms.ValidationError("The description should not contain the category name.")

        return cleaned_data
