from django import forms
from .models import Product, ProductVariant
from .models import Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'Product_name', 
            'Product_description', 
            'Product_category', 
            'Product_brand', 
            'price', 
            'offer_price', 
            'is_active'
        ]

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be less than 0.")
        return price

    def clean_offer_price(self):
        offer_price = self.cleaned_data.get('offer_price')
        price = self.cleaned_data.get('price')

        if offer_price is not None and offer_price < 0:
            raise forms.ValidationError("Offer price cannot be less than 0.")

        if price is not None and offer_price >= price:
            raise forms.ValidationError("Offer price must be less than the regular price.")

        return offer_price


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'stock', 'price', 'offer_price', 'variant_status']
        widgets = {
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'variant_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values if necessary
        if self.initial.get('size') is None:
            self.initial['size'] = ''

    # Validation for 'size'
    def clean_size(self):
        size = self.cleaned_data.get('size')
        if not size:
            raise forms.ValidationError("Size is required.")
        if not size.isalnum():  # Only allow alphanumeric size values
            raise forms.ValidationError("Size must be alphanumeric.")
        return size

    # Validation for 'stock'
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError("Stock is required.")
        if stock < 0:
            raise forms.ValidationError("Stock must be a non-negative value.")
        return stock

    # Validation for 'price'
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Price is required.")
        if price <= 0:
            raise forms.ValidationError("Price must be a positive value.")
        return price

    # Validation for 'offer_price'
    def clean_offer_price(self):
        offer_price = self.cleaned_data.get('offer_price')
        price = self.cleaned_data.get('price')

        if offer_price is None:
            raise forms.ValidationError("Offer price is required.")
        if offer_price <= 0:
            raise forms.ValidationError("Offer price must be a positive value.")
        if price is not None and offer_price >= price:
            raise forms.ValidationError("Offer price must be less than the regular price.")
        return offer_price

    # Validation for 'variant_status'
    def clean_variant_status(self):
        variant_status = self.cleaned_data.get('variant_status')
        if variant_status is None:
            raise forms.ValidationError("Variant status is required.")
        return variant_status





class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, i) for i in range(1, 6)] 

    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea, max_length=500, required=True)

    class Meta:
        model = Review
        fields = ['rating', 'comment']        