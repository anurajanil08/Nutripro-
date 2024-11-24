from django import forms
from .models import UserAddress

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'name', 'house_name', 'street_name', 'pin_number', 'district',
            'state', 'country', 'phone_number', 'is_default'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'house_name': forms.TextInput(attrs={'placeholder': 'House Name'}),
            'street_name': forms.TextInput(attrs={'placeholder': 'Street Name'}),
            'pin_number': forms.TextInput(attrs={'placeholder': 'PIN Code'}),
            'district': forms.TextInput(attrs={'placeholder': 'District'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'is_default': forms.CheckboxInput(),  
        }
 

