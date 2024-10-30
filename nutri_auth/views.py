from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout 
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from .forms import UserCreationForm
from .forms import LoginForm
from .models import User
import random
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta





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
            print(otp)

            request.session['temp_user_data'] = {
                'email': email,
                'username': username,
                'password': password,
                'otp': otp,
                'otp_generated_time': timezone.now().isoformat()
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


            return redirect('nutri_auth:verify-otp')  
        

    else:
        form = UserCreationForm()

    return render(request, 'authentication/signup.html', {'form': form})



def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        temp_user_data = request.session.get('temp_user_data')

        if temp_user_data:
            otp_generated_time = timezone.datetime.fromisoformat(temp_user_data['otp_generated_time'])
            current_time = timezone.now()

            if current_time > otp_generated_time + timedelta(minutes=2):
                return render(request, 'authentication/otp.html', {
                    'error': 'OTP has expired. Please request a new one.',
                })

            if entered_otp == temp_user_data['otp']:
                user = User(
                    email=temp_user_data['email'],
                    username=temp_user_data['username'],
                    is_active=True
                )
                user.set_password(temp_user_data['password'])
                user.save()

                del request.session['temp_user_data']
                login(request, user)

                return redirect('accounts:index')

            return render(request, 'authentication/otp.html', {
                'error': 'Invalid OTP. Please try again.',
            })

    return render(request, 'authentication/otp.html')


def resend_otp(request):
    temp_user_data = request.session.get('temp_user_data')
    
    if temp_user_data:
        new_otp = generate_otp()
        print(new_otp)
        temp_user_data['otp'] = new_otp
        temp_user_data['otp_generated_time'] = timezone.now().isoformat()
        request.session['temp_user_data'] = temp_user_data 

        try:
            send_mail(
                'Your New OTP Code',
                f'Your new OTP for account verification is {new_otp}.',
                settings.DEFAULT_FROM_EMAIL,
                [temp_user_data['email']],
                fail_silently=False,
            )
        except Exception as e:
            return render(request, 'authentication/otp.html', {
                'error': 'Failed to resend OTP. Please try again later.',
            })

        return render(request, 'authentication/otp.html', {
            'message': 'A new OTP has been sent to your email.'
        })

    return redirect('nutri_auth:signup')



def handlelogin(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:index')  
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()


    return render(request, "authentication/login.html", {'form': form})



def logout_view(request):

    logout(request)
    
    return redirect('nutri_auth:handlelogin') 


