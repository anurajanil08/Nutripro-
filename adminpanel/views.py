from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from nutri_auth.models import User
from django.contrib.auth import login, authenticate
from .forms import AdminLoginForm
from django.contrib.auth import logout
from .decorators import admin_required
from django.db.models import Sum, F
from order.models import Order


# Create your views here.




def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_admin:
        return redirect('adminpanel:dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None and user.is_admin:
                login(request, user)
                return redirect('adminpanel:dashboard')  
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid login credentials.')

    else:
        form = AdminLoginForm()

    return render(request, 'adminside/dashboard/login.html', {'form': form})

@admin_required
def dashboard(request):
  return render(request,"adminside/dashboard/dashboard.html")

@admin_required
def list_users(request):
    users = User.objects.filter(is_admin=False) 
    return render(request, 'adminside/user/userlist.html', {'users': users})

@admin_required
def toggle_user_active(request, user_id):
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()

    if user.is_active:
        messages.success(request, "User activated successfully.")
    else:
        messages.success(request, "User deactivated successfully.")
    
    return redirect('adminpanel:userlist')


@admin_required
def custom_logout_view(request):
    logout(request)
    return redirect('adminpanel:adminlogin')


# def demo(request):
#   return render(request,"base.html")

@admin_required
def sales_report(request):
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    orders = Order.objects.all()

    
    if start_date and  end_date:
        orders = orders.filter(date__range=[start_date, end_date])
    if month and year:
        orders = orders.filter(date__month=month, date__year=year)
    
    months = {
        '1': 'January', '2': 'February', '3': 'March', '4': 'April',
        '5': 'May', '6': 'June', '7': 'July', '8': 'August',
        '9': 'September', '10': 'October', '11': 'November', '12': 'December'
    }

    context = {
        'orders': orders,
        'months': months
    }
    

    return render(request, 'adminside/sales.html', context)


