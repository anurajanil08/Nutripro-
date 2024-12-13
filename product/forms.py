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
        ]

    
    def clean_Product_name(self):
        product_name = self.cleaned_data.get('Product_name')
        if not product_name:
            raise forms.ValidationError("Product name is required.")
        if len(product_name) < 3:
            raise forms.ValidationError("Product name must be at least 3 characters long.")
        return product_name

    
    def clean_Product_description(self):
        product_description = self.cleaned_data.get('Product_description')
        if not product_description:
            raise forms.ValidationError("Product description is required.")
        if len(product_description) < 10:
            raise forms.ValidationError("Product description must be at least 10 characters long.")
        return product_description

   
    def clean_Product_category(self):
        product_category = self.cleaned_data.get('Product_category')
        if not product_category:
            raise forms.ValidationError("Please select a product category.")
        return product_category

    
    def clean_Product_brand(self):
        product_brand = self.cleaned_data.get('Product_brand')
        if not product_brand:
            raise forms.ValidationError("Please select a product brand.")
        return product_brand

   
    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('Product_name')
        product_description = cleaned_data.get('Product_description')

        if product_name and product_description:
            if product_name.lower() in product_description.lower():
                raise forms.ValidationError("Product description should not contain the product name.")

        return cleaned_data


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
       
        if self.initial.get('size') is None:
            self.initial['size'] = ''

    
    def clean_size(self):
        size = self.cleaned_data.get('size')
        if not size:
            raise forms.ValidationError("Size is required.")
        if not size.isalnum(): 
            raise forms.ValidationError("Size must be alphanumeric.")
        return size

    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError("Stock is required.")
        if stock < 0:
            raise forms.ValidationError("Stock must be a non-negative value.")
        return stock

    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Price is required.")
        if price <= 0:
            raise forms.ValidationError("Price must be a positive value.")
        return price

    
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