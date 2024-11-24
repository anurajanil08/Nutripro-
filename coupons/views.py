from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Coupon
from .forms import CouponForm
import json

# Helper function to check if the user is an admin
def admin_check(user):
    return user.is_authenticated and user.is_admin

# List all coupons
@login_required
@user_passes_test(admin_check)
def admin_coupon_list(request):
    coupons = Coupon.objects.order_by('-id')  
    return render(request, 'adminside/coupons/coupon_list.html', {'coupons': coupons})

# Create a new coupon
@login_required
@user_passes_test(admin_check)
def admin_create_coupon(request, id=None):
    if id:  # If there's an id, it's for editing an existing coupon
        coupon = get_object_or_404(Coupon, id=id)
        action = 'Edit'
    else:
        coupon = None
        action = 'Create'

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)  # If editing, the instance is passed
        if form.is_valid():
            form.save()
            if id:
                messages.success(request, 'Coupon updated successfully.')
            else:
                messages.success(request, 'Coupon created successfully.')
            return redirect('coupons:coupon_list')  # Redirect to the coupon list page
        else:
            messages.error(request, 'Error saving coupon.')
    else:
        form = CouponForm(instance=coupon)  # Pre-fill the form if editing

    return render(request, 'adminside/coupons/edit_coupon.html', {
        'form': form,
        'action': action,
    })

# Toggle the status of a coupon
@login_required
@user_passes_test(admin_check)
def admin_toggle_coupon_status(request, id):
    print("hi")
    """Toggle the is_active status of a coupon."""
    coupon = get_object_or_404(Coupon, id=id)
    print(coupon)

    # Toggle the is_active field
    coupon.is_active = not coupon.is_active
    coupon.save()

    # Add a success message
    messages.success(
        request,
        f"Coupon '{coupon.name}' has been {'activated' if coupon.is_active else 'deactivated'}."
    )

    # Redirect to the coupon list page or any other page
    return redirect('coupons:coupon_list')  # Replace 'coupon_list' with the actual name of your coupon list view
@login_required
@user_passes_test(admin_check)
def admin_generate_coupon_code(request):
    import random, string
    length = 8
    coupon_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return JsonResponse({'coupon_code': coupon_code})

#userside

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        # Parse the JSON data
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')
        order_amount = float(data.get('order_amount', 0))  # Assuming order_amount is passed

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})

        # Check if the coupon is valid
        if not coupon.is_valid():
            return JsonResponse({'success': False, 'message': 'Coupon is not valid or expired.'})

        # Check minimum order amount
        if order_amount < coupon.minimum_order_amount:
            return JsonResponse({
                'success': False,
                'message': f'Minimum order amount is ₹{coupon.minimum_order_amount}.'
            })

        # Calculate discount
        discount = min(order_amount * (coupon.discount_percentage / 100), coupon.max_discount_amount)
        return JsonResponse({'success': True, 'discount': discount})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def list_active_coupons(request):
    active_coupons = Coupon.objects.filter(is_active=True, expiry_date__gt=timezone.now())
    return render(request, 'userside/coupons/list_coupons.html', {'coupons': active_coupons})


