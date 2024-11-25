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
from .signals import otp_signal
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
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

            request.session['temp_user_data'] = {
                'email': email,
                'username': username,
                'password': password,
            }
            
            otp_signal.send(sender=signup, user_data=request.session['temp_user_data'])

            return redirect('nutri_auth:verify-otp')

    else:
        form = UserCreationForm(request.POST or None)

    return render(request, 'authentication/signup.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        print("hi post")
        entered_otp = request.POST.get('otp')
        temp_user_data = request.session.get('temp_user_data')
        print("entered_otp", entered_otp)
        
        if not temp_user_data:
            messages.error(request, 'Registration session expired. Please register again.')
            return redirect('nutri_auth:register')  
        
        try:
            otp_generated_time = timezone.datetime.fromisoformat(temp_user_data['otp_generated_time'])
            current_time = timezone.now()
            
            
            if current_time > otp_generated_time + timedelta(minutes=2):
                messages.error(request, 'OTP has expired. Please request a new one.')
                return render(request, 'userside/verification-otp.html')  
            print("otp verify")
            print("temp_user_data['otp']", temp_user_data['otp'])
            if int(entered_otp) == int(temp_user_data['otp']):
                print("hi otp")
                user = User(
                    email=temp_user_data['email'],
                    username=temp_user_data['username'],
                    is_active=True
                )
                user.set_password(temp_user_data['password'])
                user.save()

                del request.session['temp_user_data']

                login(request, user)
                messages.success(request, 'Registration successful! Welcome aboard!')
                return redirect('accounts:index')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'userside/verification-otp.html')  
                
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            return render(request, 'authentication/otp.html')  
      
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
                messages.success(request, "login sucessfull")
                return redirect('accounts:index')  
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, "authentication/login.html", {'form': form})



def logout_view(request):

    logout(request)
    
    return redirect('nutri_auth:handlelogin') 


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            subject = "Password Reset Requested"
            email_template_name = "authentication/reset_email.txt"
            
            
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            
            c = {
                "email": user.email,
                'domain': domain,
                'site_name': 'NUTRI PRO',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': protocol,
            }
            
            
            email_content = render_to_string(email_template_name, c)
            
            
            send_mail(
                subject,
                email_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            
            messages.success(request, "A password reset email has been sent to your email address.")
            return redirect('nutri_auth:handlelogin')  
            
        except User.DoesNotExist:
            
            messages.error(request, "No user found with this email address.")
            return redirect('nutri_auth:forgot_password')

    
    return render(request, 'authentication/forgot_password.html')



def reset_password(request, uidb64, token):
    try:
        user_id = force_bytes(urlsafe_base64_decode(uidb64)).decode()
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully!")
                return redirect('nutri_auth:handlelogin')  
        else:
            form = SetPasswordForm(user)
        return render(request, 'authentication/reset_password.html', {
            'form': form,
            'title': 'Reset Password',
            'instructions': 'Please enter your new password below.',
        })
    else:
        messages.error(request, "The password reset link is invalid or has expired. Please request a new one.")
        return redirect('nutri_auth:forgot_password')
