from django import forms
from django.core.exceptions import ValidationError
from .models import User
from django.contrib.auth import get_user_model
import re
from django.contrib.auth import authenticate

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    
    # def clean_password1(self):
    #     password = self.cleaned_data.get("password1")
    #     if not re.search(r"[A-Z]", password):
    #         raise ValidationError("Password must contain at least one uppercase letter.")
    #     if not re.search(r"[a-z]", password):
    #         raise ValidationError("Password must contain at least one lowercase letter.")
    #     if not re.search(r"[0-9]", password):
    #         raise ValidationError("Password must contain at least one number.")
    #     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #         raise ValidationError("Password must contain at least one special character.")
    #     return password
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user





class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))
