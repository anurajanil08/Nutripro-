from django import forms
import re
from .models import Brand


class BrandForm(forms.ModelForm):
    brand_name = forms.CharField(
        min_length=2,
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter brand name'
        }),
        error_messages={
            'required': 'Brand name is required',
            'min_length': 'Brand name must be at least 2 characters long',
            'max_length': 'Brand name cannot exceed 40 characters'
        }
    )
    
    description = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter brand description'
        }),
        error_messages={
            'required': 'Description is required',
            'max_length': 'Description cannot exceed 255 characters'
        }
    )
    
    status = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = Brand
        fields = ['brand_name', 'description', 'status']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        if instance:
            # Update widget attributes with current values
            self.fields['brand_name'].widget.attrs.update({
                'value': instance.brand_name
            })
            # For textarea, set the initial value
            self.fields['description'].widget.attrs.update({
                'value': instance.description,
            })
            # Set the actual content for the textarea
            self.initial['description'] = instance.description
            # Set status
            self.fields['status'].initial = instance.status

    def clean_brand_name(self):
        """
        Validation for brand_name: Only allows alphabets and spaces.
        """
        brand_name = self.cleaned_data.get('brand_name')
        if not re.match(r'^[A-Za-z\s]+$', brand_name):  
            raise forms.ValidationError("Brand name should contain only alphabets and spaces.")
        return brand_name

    def clean_description(self):
        """
        Validation for description: Minimum length of 10 characters.
        """
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError("Description must be at least 10 characters long.")
        return description
