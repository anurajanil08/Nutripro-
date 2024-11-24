from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import Order, OrderItem, OrderAddress
from product.models import ProductVariant
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import UserAddress
from cart.models import Cart,CartItem
import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from wallet.models import Wallet, WalletTransaction


@login_required
def place_order(request):
    user = request.user
    user_cart = Cart.objects.filter(user=user).first()
    cart_items = CartItem.objects.filter(cart=user_cart, is_active=True)
    address_id = request.POST.get('address')
    payment_method = request.POST.get('payment_method')

    if not user_cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view_cart')

    if not cart_items:
        messages.error(request, "Your cart is empty. Please add items to your cart before placing an order.")
        return redirect('cart:view_cart')

    if not address_id:
        messages.error(request, "Please select an address.")
        return redirect('checkout')

    
    user_address = get_object_or_404(UserAddress, id=address_id, user=user)

    
    order_address = OrderAddress.objects.create(
        name=user_address.name,
        house_name=user_address.house_name,
        street_name=user_address.street_name,
        pin_number=user_address.pin_number,
        district=user_address.district,
        state=user_address.state,
        country=user_address.country,
        phone_number=user_address.phone_number,
        status=True
    )

    
    total_amount = 0
    for item in cart_items:
        item_total = Decimal(item.variant.price) * item.quantity
        item.item_total = item_total
        total_amount += item_total

    discount_amount = Decimal("10.00")
    final_amount = total_amount - discount_amount

    if payment_method == 'cashondelivery':
        
        order = Order.objects.create(
            user=user,
            address=order_address,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            order_id=f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            date=timezone.now(),
            payment_option='cashondelivery',
            order_status='Pending'
        )

        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.price,
                status="Ordered"
            )

        
        user_cart.items.all().delete()

        
        return render(request, 'userside/order/order_placed.html', {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'order': order,
        })

    elif payment_method == 'razorpay':
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(final_amount * 100),  
            'currency': 'INR',
            'payment_capture': '1'
        })

        
        order = Order.objects.create(
            user=user,
            address=order_address,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            order_id=f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            date=timezone.now(),
            payment_option='razorpay',
            order_status='Pending',
            payment_id=razorpay_order['id']
        )

        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.price,
                status="Ordered"
            )

        
        user_cart.items.all().delete()

        
        return render(request, 'userside/cart/razorpay_checkout.html', {
            'order': order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'final_amount': final_amount,
        })
    
    elif payment_method == 'wallet':
        # Process Wallet Payment
        wallet = Wallet.objects.get(user=user)

        # Check if the wallet has sufficient balance
        if wallet.balance < final_amount:
            messages.error(request, "You don't have enough balance in your wallet to complete this purchase.")
            return redirect('cart:checkout')  # Redirect to checkout page to choose a different payment method

        # Deduct the amount from the wallet balance
        wallet.balance -= final_amount
        wallet.save()
        order_id =f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        # Create a Wallet Transaction to log the payment
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=final_amount,
            description=f"Payment for Order #{order_id}",
            transaction_type='debit',
        )

        # Create the Order
        order = Order.objects.create(
            user=user,
            address=order_address,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            order_id=order_id,
            date=timezone.now(),
            payment_option='wallet',
            order_status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.price,
                status="Ordered"
            )

        user_cart.items.all().delete()

        return render(request, 'userside/order/order_placed.html', {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'order': order,
        })


    else:
        
        messages.error(request, "Invalid payment method selected.")
        return redirect('cart:checkout')







# @login_required
# def order_details(request, order_id):
#     order = get_object_or_404(Order, order_id=order_id, user=request.user)
#     items = order.items.all()
#     context = {
#         'order': order,
#         'items': items
#     }
#     return render(request, 'orders/order_details.html', context)


# @login_required
# def order_list(request):
#     orders = Order.objects.filter(user=request.user).order_by('-date')
#     context = {
#         'orders': orders
#     }
#     return render(request, 'orders/order_list.html', context)




# @staff_member_required
# def update_order_status(request, order_id):
#     order = get_object_or_404(Order, order_id=order_id)
#     if request.method == "POST":
#         new_status = request.POST.get('status')
#         if new_status in dict(Order.ORDER_STATUS_CHOICES):
#             order.order_status = new_status
#             order.save()
#             messages.success(request, f"Order #{order.order_id} status updated to {new_status}.")
#         else:
#             messages.error(request, "Invalid status.")
#     return redirect('admin_order_list')


def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')  
    print(orders)
    return render(request, 'userside/order/order_list.html', {'orders': orders})

# def order_details(request, order_id):
#     order = Order.objects.get(id=order_id, user=request.user)
#     items = order.items.all()  
#     return render(request, 'userside/orders/order_details.html', {'order': order, 'items': items})

# def cancel_order(request, order_id):
#     """
#     View to cancel an order by updating the order status to 'Cancelled'.
#     """
#     if request.method == "POST":
#         order = get_object_or_404(Order, id=order_id)
        
       
#         if order.order_status != 'Cancelled':
#             order.order_status = 'Cancelled'  
#             order.save()  
        
        
#         return redirect('order:order_list')  

#     return redirect('userside/order/order_list')  


def cancel_order(request, order_id):
    """
    View to cancel an order and refund the amount to the user's wallet.
    """
    if request.method == "POST":
        
        order = get_object_or_404(Order, id=order_id)

        
        if order.order_status != 'Cancelled':
            
            order.order_status = 'Cancelled'
            order.save()

            
            try:
                
                wallet = Wallet.objects.get(user=order.user)

                
                refund_amount = order.final_amount

                
                wallet.credit(refund_amount)

                
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=refund_amount,
                    description=f"Refund for canceled order #{order.order_id}",
                    transaction_type="credit",
                )

                
                messages.success(request, f"Order #{order.order_id} has been canceled. ₹{refund_amount} refunded to your wallet.")
            except Wallet.DoesNotExist:
                
                messages.error(request, "Refund failed as the user does not have a wallet.")
        else:
            
            messages.info(request, "Order is already canceled.")

        
        return redirect('order:order_list')

    
    return redirect('userside/order/order_list')









#admin

def admin_order_list(request):
    orders = Order.objects.all().order_by('-date')  
    return render(request, 'adminside/order/ad_order_list.html', {'orders': orders})

def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.order_status = new_status
        order.save()
        return redirect('order:admin_order_list') 
    return render(request, 'adminside/order/update_order.html', {'order': order})

def adorder_details(request, order_id):
    """
    View to display order details for the admin panel.
    """
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'adminside/order/order_details.html', context)


#Razorpay


client = razorpay.Client(auth=('RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET'))

@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            
            amount = 50000  
            currency = "INR"

            
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": currency,
                "payment_capture": 1 
            })

            return JsonResponse({
                "order_id": razorpay_order["id"],
                "amount": amount,
                "currency": currency,
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            # Verify payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            # Update order status
            order = Order.objects.get(payment_id=data['razorpay_order_id'])
            order.payment_status = True
            order.order_status = 'Completed'
            order.save()

            # Render the order placed page with order details
            messages.success(request, "Payment successful!")
            return render(request, 'userside/order/order_placed.html', {'order': order})

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed!")
            return render(request, 'userside/order/payment_failed.html', {})

    messages.error(request, "Invalid payment request.")
    return render(request, 'userside/order/payment_failed.html', {})