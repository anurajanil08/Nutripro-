from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from nutri_auth.models import User
from django.contrib.auth import login, authenticate
from .forms import AdminLoginForm
from django.contrib.auth import logout
from .decorators import admin_required
from django.db.models import Sum, F
from order.models import Order
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from io import BytesIO
from django.core.paginator import Paginator
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
import json
from django.db.models import Count
from category.models import Category
from brand.models import Brand
from product.models import Product
from django.http import JsonResponse
from django.db.models.functions import TruncDate





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
   top_categories = Category.get_top_10_categories()
   top_brands = Brand.get_top_10_brands()
   top_products = Product.get_top_10_best_selling_products()

   context = {
        'top_categories': top_categories,
        'top_brands': top_brands,
        'top_products': top_products,
    }
  
   return render(request,"adminside/dashboard/dashboard.html", context)

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






@admin_required
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    page_number = request.GET.get('page', 1)

    orders = Order.objects.all()
     
    if start_date and end_date and start_date == end_date:
        try:
            single_day = datetime.strptime(start_date, "%Y-%m-%d").date()
            orders = orders.annotate(date_only=TruncDate('date')).filter(date_only=single_day)
        except ValueError:
            pass  

    
    elif start_date and end_date:
        try:
            orders = orders.filter(date__range=[start_date, end_date])
        except ValueError:
            pass  

    
    if month and year:
        orders = orders.filter(date__month=month, date__year=year)

    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
 

    paginator = Paginator(orders, 10)  
    page_obj = paginator.get_page(page_number)

    
    if 'generate_pdf' in request.GET:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        
        pdf.drawString(100, 750, "Sales Report")
        y = 720
        pdf.drawString(100, y, f"Start Date: {start_date or 'N/A'}")
        y -= 20
        pdf.drawString(100, y, f"End Date: {end_date or 'N/A'}")
        y -= 40

        
        pdf.drawString(100, y, "ID")
        pdf.drawString(200, y, "Customer Name")
        pdf.drawString(350, y, "Total Price")
        pdf.drawString(500, y, "Date")
        y -= 20

        for order in orders:
            pdf.drawString(100, y, str(order.id))
            pdf.drawString(200, y, getattr(order.address, "name", "N/A"))
            pdf.drawString(350, y, f"{order.total_amount}")
            pdf.drawString(500, y, order.date.strftime("%Y-%m-%d"))
            y -= 20
            if y < 50:  
                pdf.showPage()
                y = 750
        pdf.drawString(100, y - 40, f"Total Sales: {total_sales}")

        pdf.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        return response

    
    if 'generate_excel' in request.GET:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Sales Report"

        headers = ["ID", "Customer Name", "Total Price", "Date"]
        worksheet.append(headers)

        
        for order in orders:
            worksheet.append([
                order.id,
                getattr(order.address, "name", "N/A"),
                order.total_amount,
                order.date.strftime("%Y-%m-%d"),
            ])
        worksheet.append(["", "Total Sales", total_sales, ""])    

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
        workbook.save(response)
        return response

   
    months = {
        '1': 'January', '2': 'February', '3': 'March', '4': 'April',
        '5': 'May', '6': 'June', '7': 'July', '8': 'August',
        '9': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    selected_month = months.get(month, "Not Selected")

    context = {
        'page_obj': page_obj,
        'months': months,
        'start_date': start_date,
        'end_date': end_date,
        'month': month,
        'year': year,
        "selected_month": selected_month,
        "total_sales": total_sales,
    }
    return render(request, 'adminside/sales.html', context)





def chart_data_view(request):
    filter_type = request.GET.get('filter', 'monthly')  
    summary_data = Order.sales_summary(filter_type)
    
    chart_data = {
        "labels": [entry["label"] for entry in summary_data],
        "data": [entry["sales"] for entry in summary_data],
    }
    return JsonResponse(chart_data)
