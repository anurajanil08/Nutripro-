from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import User
from django.conf import settings
import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserCreationForm



# Create your views here.


User = get_user_model()  

def generate_otp():
    return str(random.randint(100000, 999999))

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            otp = generate_otp()

            request.session['temp_user_data'] = {
                'email': email,
                'username': username,
                'password': password,
                'otp': otp
            }

            try:
                send_mail(
                    'Your OTP Code',
                    f'Your OTP for account verification is {otp}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                form.add_error(None, "Failed to send the OTP. Please try again.")
                return render(request, 'authentication/signup.html', {'form': form})


            return redirect('verify_otp')  

    else:
        form = UserCreationForm()

    return render(request, 'authentication/signup.html', {'form': form})



def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        temp_user_data = request.session.get('temp_user_data')

        if temp_user_data and entered_otp == temp_user_data['otp']:
            user = User(
                email=temp_user_data['email'],
                username=temp_user_data['username'],
                is_active=True
            )
            user.set_password(temp_user_data['password'])
            user.save()

            del request.session['temp_user_data']

            login(request, user)

            return redirect('index')  

        else:
            return render(request, 'authentication/verify_otp.html', {
                'error': 'Invalid OTP. Please try again.',
            })

    return render(request, 'authentication/verify_otp.html')




def handlelogin(request):
  return render(request,"authentication/login.html")  



def otp(request):
    if request.method == 'POST':
        otp_value = request.POST.get('otp')

    return render(request,"authentication/otp.html")  

def handlelogout(request):
  return redirect(request,'/auth/login') 