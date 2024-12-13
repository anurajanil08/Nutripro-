from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Coupon,CouponUsage
from .forms import CouponForm
import json
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP




@login_required

def admin_coupon_list(request):
    coupons = Coupon.objects.order_by('-id')  
    return render(request, 'adminside/coupons/coupon_list.html', {'coupons': coupons})


@login_required

def admin_create_coupon(request, id=None):
    if id: 
        coupon = get_object_or_404(Coupon, id=id)
        action = 'Edit'
    else:
        coupon = None
        action = 'Create'

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)  
        if form.is_valid():
            form.save()
            if id:
                messages.success(request, 'Coupon updated successfully.')
            else:
                messages.success(request, 'Coupon created successfully.')
            return redirect('coupons:coupon_list')  
        else:
            messages.error(request, 'Error saving coupon.')
    else:
        form = CouponForm(instance=coupon)  

    return render(request, 'adminside/coupons/edit_coupon.html', {
        'form': form,
        'action': action,
    })



@login_required
def admin_toggle_coupon_status(request, id):

    coupon = get_object_or_404(Coupon, id=id)

    
    coupon.is_active = not coupon.is_active
    coupon.save()

    
    messages.success(
        request,
        f"Coupon '{coupon.name}' has been {'activated' if coupon.is_active else 'deactivated'}."
    )

    
    return redirect('coupons:coupon_list')  




#user side



# def apply_coupon(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             coupon_code = data.get("coupon_code")
            
#             order_amount = Decimal(str(data.get("order_amount")))

            
#             coupon = get_object_or_404(Coupon, code=coupon_code)

#             print(coupon)

            
#             if order_amount < Decimal(str(coupon.minimum_order_amount)):
#                 return JsonResponse({
#                     "success": False, 
#                     "message": f"Minimum order amount is ₹{coupon.minimum_order_amount}"
#                 })

            
#             discount_percentage = Decimal(str(coupon.discount_percentage)) / Decimal('100')

#             print(discount_percentage)
#             discount = min(
#                 discount_percentage * order_amount, 
#                 Decimal(str(coupon.max_discount_amount))
#             ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#             print("discount",discount)

            
#             final_total = (order_amount - discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#             print("final_total",final_total)

            
#             request.session['applied_coupon'] = {
#                 'code': coupon.code,
#                 'discount': float(discount),  
#                 'final_total': float(final_total)
#             }

#             return JsonResponse({
#                 "success": True,
#                 "discount": float(discount),
#                 "final_total": float(final_total),
#                 "message": f"Coupon {coupon_code} applied successfully!"
#             })

#         except Coupon.DoesNotExist:
#             return JsonResponse({
#                 "success": False, 
#                 "message": "Invalid coupon code."
#             })
#         except (TypeError, ValueError) as e:
#             return JsonResponse({
#                 "success": False, 
#                 "message": f"Invalid input: {str(e)}"
#             })
#         except Exception as e:
#             return JsonResponse({
#                 "success": False, 
#                 "message": str(e)
#             })

#     return JsonResponse({
#         "success": False, 
#         "message": "Invalid request method."
#     })

def apply_coupon(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            coupon_code = data.get("coupon_code")
            order_amount = Decimal(str(data.get("order_amount")))

            
            coupon = get_object_or_404(Coupon, code=coupon_code)

            
            if not coupon.is_active:
                return JsonResponse({
                    "success": False,
                    "message": "This coupon is inactive."
                })

            
            if coupon.expiry_date < timezone.now():
                return JsonResponse({
                    "success": False,
                    "message": "This coupon has expired."
                })

            
            if order_amount < Decimal(str(coupon.minimum_order_amount)):
                return JsonResponse({
                    "success": False,
                    "message": f"Minimum order amount is ₹{coupon.minimum_order_amount}."
                })

            
            discount_percentage = Decimal(str(coupon.discount_percentage)) / Decimal('100')
            discount = min(
                discount_percentage * order_amount,
                Decimal(str(coupon.max_discount_amount))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            
            final_total = (order_amount - discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            
            request.session['applied_coupon'] = {
                'code': coupon.code,
                'discount': float(discount),  
                'final_total': float(final_total)
            }

            return JsonResponse({
                "success": True,
                "discount": float(discount),
                "final_total": float(final_total),
                "message": f"Coupon {coupon_code} applied successfully!"
            })

        except Coupon.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Invalid coupon code."
            })
        except (TypeError, ValueError) as e:
            return JsonResponse({
                "success": False,
                "message": f"Invalid input: {str(e)}"
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            })

    return JsonResponse({
        "success": False,
        "message": "Invalid request method."
    })



def remove_coupon(request):
    if request.method == "POST":
        
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        
        return JsonResponse({
            "success": True,
            "message": "Coupon removed successfully."
        })

@login_required
def list_active_coupons(request):
    active_coupons = Coupon.objects.filter(is_active=True, expiry_date__gt=timezone.now())
    return render(request, 'userside/coupons/list_coupons.html', {'coupons': active_coupons})


