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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or name.strip() == '' or not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Please enter a valid name. Only alphabets are allowed.")
        return name

    def clean_house_name(self):
        house_name = self.cleaned_data.get('house_name')
        if not house_name or house_name.strip() == '' or not house_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Please enter a valid Housename. Only alphabets are allowed.")
        return house_name

    def clean_street_name(self):
        street_name = self.cleaned_data.get('street_name')
        if not street_name or street_name.strip() == '' or not street_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Please enter a valid street name.")
        return street_name

    def clean_pin_number(self):
        pin_number = self.cleaned_data.get('pin_number')
        if not pin_number or not pin_number.isdigit() or len(pin_number) != 6:
            raise forms.ValidationError("Please enter a valid 6-digit PIN code.")
        return pin_number

    def clean_district(self):
        district = self.cleaned_data.get('district')
        if not district or district.strip() == '' or not district.isalpha():
            raise forms.ValidationError("Please enter a valid district name. Only alphabets are allowed.")
        return district

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state or state.strip() == '' or not state.isalpha():
            raise forms.ValidationError("Please enter a valid state name. Only alphabets are allowed.")
        return state

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country or country.strip() == '' or not country.isalpha():
            raise forms.ValidationError("Please enter a valid country name. Only alphabets are allowed.")
        return country

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) == 10 and not phone_number or not phone_number.isdigit() :
            raise forms.ValidationError("Please enter a valid phone number of  10 digits")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data





