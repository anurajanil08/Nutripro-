from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class AdminLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)

        if user is None:
            raise forms.ValidationError('Invalid email or password.')
        elif not user.is_admin:
            raise forms.ValidationError('You do not have admin rights.')

        return self.cleaned_data
