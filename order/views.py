from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import Order, OrderItem, OrderAddress
from product.models import ProductImages
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import UserAddress
from cart.models import Cart,CartItem
import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from wallet.models import Wallet, WalletTransaction
from coupons.models import Coupon ,CouponUsage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import ReturnOrder
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from .models import Order, OrderItem
from reportlab.lib.units import inch
from .models import Order


@login_required
def place_order(request):
    user = request.user
    user_cart = Cart.objects.filter(user=user).first()
    cart_items = CartItem.objects.filter(cart=user_cart)
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

    total_amount = Decimal('0.00') 
    discount_amount = Decimal('0.00')  
    final_amount = Decimal('0.00')  

    for item in cart_items:
        item_total = Decimal(item.sub_total())
        total_amount += item_total
        original_price_total = Decimal(item.variant.price) * item.quantity
        item_discount = original_price_total - item_total 

    final_amount = total_amount

    print("Total Amount (before discounts):", total_amount + discount_amount)
    print("Discount Amount:", discount_amount)
    print("Final Amount (after discounts):", final_amount)

    
    applied_coupon = request.session.get('applied_coupon')
    coupon = None

    if applied_coupon:
        print("coupon applied")
        try:
            
            coupon = Coupon.objects.get(code=applied_coupon['code'])
            
            
            discount_amount = Decimal(str(applied_coupon['discount']))
            final_amount = Decimal(str(applied_coupon['final_total']))
        except Coupon.DoesNotExist:
            
            messages.warning(request, "Applied coupon is no longer valid.")
            
            if 'applied_coupon' in request.session:
                del request.session['applied_coupon']
        except Exception as e:
            messages.error(request, f"Error applying coupon: {str(e)}")

    if payment_method == 'cashondelivery':
        if final_amount > 1000:
            messages.error(request, "Cash on Delivery is not available for orders above ₹1000. Please select a different payment method.")
            return redirect('cart:checkout')


        
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
            item.variant.stock -= item.quantity
            item.variant.save()    

        
        user_cart.items.all().delete()

        if coupon:
            
            coupon_usage, created = CouponUsage.objects.get_or_create(
                user=user,
                coupon=coupon
            )
            coupon_usage.times_used += 1
            coupon_usage.save()

            
            coupon.usage_count += 1
            coupon.save()

        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        
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
            item.variant.stock -= item.quantity
            item.variant.save()   


        

        
        user_cart.items.all().delete()


        if coupon:
            
            coupon_usage, created = CouponUsage.objects.get_or_create(
                user=user,
                coupon=coupon
            )
            coupon_usage.times_used += 1
            coupon_usage.save()

            
            coupon.usage_count += 1
            coupon.save()

        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        
        return render(request, 'userside/cart/razorpay_checkout.html', {
            'order': order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'final_amount': final_amount,
        })
    
    elif payment_method == 'wallet':

        wallet = Wallet.objects.get(user=user)

        
        if wallet.balance < final_amount:
            messages.error(request, "You don't have enough balance in your wallet to complete this purchase.")
            return redirect('cart:checkout')  

        
        wallet.balance -= final_amount
        wallet.save()
        order_id =f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=final_amount,
            description=f"Payment for Order #{order_id}",
            transaction_type='debit',
        )

        
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
            item.variant.stock -= item.quantity
            item.variant.save()    

        user_cart.items.all().delete()

        if coupon:
            
            coupon_usage, created = CouponUsage.objects.get_or_create(
                user=user,
                coupon=coupon
            )
            coupon_usage.times_used += 1
            coupon_usage.save()

           
            coupon.usage_count += 1
            coupon.save()

        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        return render(request, 'userside/order/order_placed.html', {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'order': order,
        })


    else:
        
        messages.error(request, "Invalid payment method selected.")
        return redirect('cart:checkout')




def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')
    for order in orders:
        print(f"Order ID: {order.order_id}")  
    return render(request, 'userside/order/order_list.html', {'orders': orders})




def cancel_order(request, order_id):
        
    order = get_object_or_404(Order, id=order_id)
    
    if order.order_status != 'Cancelled':
        
        order.order_status = 'Cancelled'
        order.save()

        if order.payment_option=="razorpay" or order.payment_option=="wallet":
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
                return redirect('order:order_list')
            except Wallet.DoesNotExist:
            
                messages.error(request, "Refund failed as the user does not have a wallet.")
    else:
        
        messages.info(request, "Order is already canceled.")

        
        return redirect('order:order_list')

    
    return redirect('userside/order/order_list')



#    



@login_required
def order_details(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    order_items = order.items.all()

    for item in order_items:
        first_image = item.variant.Product.productimages_set.first()
        item.first_image_url = first_image.images.url if first_image else None

    return render(request, 'userside/order/order_details.html', {
        'order': order,
        'order_items': order_items,
    })



#admin

def admin_order_list(request):
    orders = Order.objects.all().order_by('-id')  
    return render(request, 'adminside/order/ad_order_list.html', {'orders': orders})




def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id) 
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
       
        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            order.order_status = new_status
            
            
            if new_status == 'Delivered':
                order.payment_status = True
            
            order.save() 
            messages.success(request, "Order status updated successfully.")
            return redirect('order:admin_order_list') 
        else:
            messages.error(request, "Invalid status selected.")
    
   
    return render(request, 'adminside/order/update_order.html', {
        'order': order,
        'status_choices': Order.ORDER_STATUS_CHOICES,
    })

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
            
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            
            order = Order.objects.get(payment_id=data['razorpay_order_id'])
            order.payment_status = True
            order.order_status = 'Completed'
            order.save()

           
            messages.success(request, "Payment successful!")
            return render(request, 'userside/order/order_placed.html', {'order': order})

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed!")
            return render(request, 'userside/order/payment_failed.html', {})

    messages.error(request, "Invalid payment request.")
    return render(request, 'userside/order/payment_failed.html', {})
#####






def download_invoice(request, order_id):
    try:
        
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)

        buffer = BytesIO()

        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))

        
        def draw_text(x, y, text, font_name='Vera', font_size=12, color=colors.black):
            p.setFont(font_name, font_size)
            p.setFillColor(color)
            p.drawString(x, y, text)

        
        p.setFillColorRGB(0.2, 0.2, 0.2)
        p.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1)
        draw_text(0.5*inch, height - inch, "INVOICE", 'Vera', 36, colors.white)
        draw_text(width - 2.5*inch, height - 0.75*inch, f"Order #{order.order_id}", 'Vera', 16, colors.white)

        
        draw_text(0.5*inch, height - 2*inch, "Nutripro", 'Vera', 18)
        
        draw_text(0.5*inch, height - 2.5*inch, "Ernakulam, Kerala, 682304", 'Vera', 12)
        draw_text(0.5*inch, height - 2.7*inch, "Phone: 8301025681", 'Vera', 12)

        
        draw_text(0.5*inch, height - 3.5*inch, "Bill To:", 'Vera', 14)
        draw_text(0.5*inch, height - 3.8*inch, order.address.name, 'Vera', 12)
        draw_text(0.5*inch, height - 4*inch, f"{order.address.house_name}, {order.address.street_name}", 'Vera', 12)
        draw_text(0.5*inch, height - 4.2*inch, f"{order.address.district}, {order.address.state}", 'Vera', 12)
        draw_text(0.5*inch, height - 4.4*inch, f"{order.address.country}, PIN: {order.address.pin_number}", 'Vera', 12)

        
        draw_text(width - 2.5*inch, height - 3.5*inch, f"Date: {order.date.strftime('%B %d, %Y')}", 'Vera', 12)
        draw_text(width - 2.5*inch, height - 3.8*inch, f"Status: {order.order_status}", 'Vera', 12)
        draw_text(width - 2.5*inch, height - 4.1*inch, f"Payment: {order.payment_option}", 'Vera', 12)

        
        data = [["Product", "Quantity", "Price", "Total"]]
        
        
        style = ParagraphStyle(
            'Normal',
            fontName='Vera',
            fontSize=10,
            leading=12,
            alignment=0,
            wordWrap='LTR'
        )

        for item in order_items:
            product_name = Paragraph(f"{item.variant.Product.Product_name} ({item.variant.size})", style)
            
            data.append([
                product_name,
                str(item.quantity),
                f"₹{item.price}",
                f"₹{item.total_cost()}"
            ])

        table = Table(data, colWidths=[3*inch, 1*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Vera'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Vera'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        table.wrapOn(p, width, height)
        table.drawOn(p, 0.5*inch, height - 6*inch)

        
        draw_text(width - 2*inch, height - 6.5*inch, f"Subtotal: ₹{order.total_amount}", 'Vera', 12)
        draw_text(width - 2*inch, height - 6.8*inch, f"Discount: ₹{order.discount_amount}", 'Vera', 12)
        p.setFillColorRGB(0.2, 0.2, 0.2)
        p.rect(width - 2.5*inch, height - 7.3*inch, 2*inch, 0.3*inch, fill=1)
        draw_text(width - 2*inch, height - 7.2*inch, f"Total: ₹{order.final_amount}", 'Vera', 14, colors.white)

      
        p.setFillColorRGB(0.2, 0.2, 0.2)
        p.rect(0, 1*inch, width, 0.5*inch, fill=1)
        draw_text(width/2 - 1.5*inch, 1.2*inch, "Thank you for your business!", 'Vera', 14, colors.white)

 
        p.showPage()
        p.save()

     
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)






@staff_member_required
def manage_returns(request):
    # if request.method == "POST":
    #     return_id = request.POST.get('return_id')
    #     return_order = get_object_or_404(ReturnOrder, id=return_id)
    #     status = request.POST.get('status')
    #     comments = request.POST.get('admin_comments')
    #     return_order.status = status
    #     return_order.admin_comments = comments
    #     return_order.save()
    #     messages.success(request, "Return status updated successfully.")
    #     return redirect('order:admin_manage_returns')

    returns = ReturnOrder.objects.order_by('-id')
    return render(request, 'adminside/order/return.html', {'returns': returns})





@staff_member_required
def update_return_status(request, return_id):
   
    
    return_order = get_object_or_404(ReturnOrder, id=return_id)
    user = return_order.order.user  

    if request.method == "POST":
       
        if return_order.status != "Pending":
            messages.error(
                request,
                f"Return request for Order #{return_order.order.order_id} has already been processed."
            )
            return redirect('order:admin_manage_returns')

        
        status = request.POST.get('status')
        comments = request.POST.get('admin_comments')
        return_order.status = status
        return_order.admin_comments = comments

        
        if status == "Approved":
            
            wallet, created = Wallet.objects.get_or_create(user=user)
            
           
            wallet.credit(return_order.order.final_amount)

            
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=return_order.order.final_amount,
                description=f"Refund for Return Order #{return_order.order.order_id}",
                transaction_type="credit"
            )

            
            messages.success(
                request,
                f"Amount {return_order.order.final_amount} credited to {user.username}'s wallet. Transaction recorded."
            )

        
        return_order.save()
        return redirect('order:admin_manage_returns')

    
    return render(request, 'adminside/order/return.html', {'return_order': return_order})





 
def request_return(request, order_id):

    order = get_object_or_404(Order, order_id=order_id)
    if ReturnOrder.objects.filter(order=order).exists():
        messages.error(request, "A return request for this order has already been submitted.")
        return redirect('order:order_detail', id=order.id) 

    if request.method == 'POST':
        reason = request.POST.get('reason')
        instructions = request.POST.get('instructions')

        
        return_order = ReturnOrder(
            order=order,
            reason=reason,

            status='Pending',  
        )
        return_order.save()

        messages.success(request, 'Your return request has been submitted.')
        return redirect('order:order_detail', id=order.id)  

    return render(request, 'userside/order/request_return.html', {'order_id': order_id})


