from django.shortcuts import render , redirect
from django.contrib.auth import get_user_model  
User = get_user_model()  



from django.shortcuts import render, get_object_or_404
from .models import productt,Cart 


# def product_detail(request, product_id):
#     product = get_object_or_404(productt, id=product_id)
   
#     return render(request, 'product.html', {'product': product })

from django.shortcuts import render, get_object_or_404, redirect
from .models import productt, Review
from .forms import ReviewForm  # Make sure you have this form created
from django.contrib.auth.decorators import login_required

def product_detail(request, product_id):
    product = get_object_or_404(productt, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')  # from related_name='reviews'

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST, request.FILES)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', product_id=product.id)
        else:
            return redirect('login')
    else:
        form = ReviewForm()

    return render(request, 'product.html', {
        'product': product,
        'form': form,
        'reviews': reviews
    })




def add_to_cart(request, product_id):
    product = get_object_or_404(productt, id=product_id)
    
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        request.session.modified = True
        print("Session Cart After Adding Product:", request.session['cart'])  

    else:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if created:
            cart_item.quantity = 1  # First time added
        else:
            cart_item.quantity += 1  # Increment only if it already exists
        cart_item.save()
        print(f"Cart Updated in DB: {cart_item.product.pname}, Quantity: {cart_item.quantity}") 

    return redirect('cart_view')


    

from django.contrib.auth import authenticate, login
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .recommendation import get_similar_products_for_cart, get_smart_category_recommendations

def cart_view(request):
    cart_items = []
    total_price = 0
    products_in_cart = []
    similar_products = []
    smart_category_products = []

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)

        for item in cart_items:
            item.subtotal = item.product.pprice * item.quantity
            total_price += item.subtotal
            products_in_cart.append(item.product)

    else:
        cart = request.session.get("cart", {})
        for product_id, quantity in cart.items():
            product = productt.objects.get(id=product_id)
            subtotal = product.pprice * quantity
            total_price += subtotal
            cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
            products_in_cart.append(product)

    # Get both recommendations
    if products_in_cart:
        similar_products = get_similar_products_for_cart(products_in_cart)
        smart_category_products = get_smart_category_recommendations(products_in_cart)

    request.session["cart_total"] = total_price
    request.session.modified = True

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "similar_products": similar_products,
        "smart_category_products": smart_category_products,
    })



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

def update_cart(request, product_id):
    if request.method == "POST":
        action = request.POST.get("action") 
        product = get_object_or_404(productt, id=product_id)

        if request.user.is_authenticated:
            # Update for logged-in users
            cart_item = Cart.objects.filter(user=request.user, product=product).first()
            # if cart_item:
            #     if action == "increase":
            #         cart_item.quantity += 1
            #     elif action == "decrease":
            #         cart_item.quantity -= 1
            #         if cart_item.quantity <= 0:
            #             cart_item.delete() 
            #     cart_item.save()
            #     print(f"Updated {cart_item.product.pname} to {cart_item.quantity}") 

            if cart_item:
                if action == "increase":
                    cart_item.quantity += 1
                    cart_item.save()
                elif action == "decrease":
                    cart_item.quantity -= 1
                    if cart_item.quantity <= 0:
                        cart_item.delete()
                        print(f"Deleted {cart_item.product.pname} from DB cart") 
                    else:
                        cart_item.save()
                        print(f"Updated {cart_item.product.pname} to {cart_item.quantity}") 

        else:
           
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                if action == "increase":
                    cart[str(product_id)] += 1
                elif action == "decrease":
                    cart[str(product_id)] -= 1
                    if cart[str(product_id)] <= 0:
                        del cart[str(product_id)]  
                request.session['cart'] = cart
                request.session.modified = True
                print(f"Updated session cart: {cart}")  

    return redirect('cart_view')




def remove_from_cart(request, product_id):
    product = get_object_or_404(productt, id=product_id)

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            cart_item.delete()
            print(f"Removed {product.pname} from DB cart") 
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            print(f"Removed {product.pname} from session cart")  
            request.session['cart'] = cart
            request.session.modified = True

    return redirect('cart_view')


from django.conf import settings









from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseBadRequest
import razorpay
from .models import Payment  # Assuming you have a Payment model

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def home(request):
    cart_total = request.session.get("cart_total", 0)
    print(f"Cart Total: {cart_total}")

    if cart_total == 0:
        return render(request, 'empty_cart.html')  # Optional: redirect if cart is empty

    currency = 'INR'
    amount = int(cart_total * 100)  # Convert to paise

    order_data = {
        "amount": amount,
        "currency": currency,
        "payment_capture": "1"
    }

    # Create Razorpay Order
    razorpay_order = client.order.create(order_data)
    print(f"Order Created: {razorpay_order}")

    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'  # URL to handle payment response

    # Save necessary data in session
    request.session['payment_amount'] = amount
    request.session['order_id'] = razorpay_order_id

    context = {
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_id': razorpay_order_id,
        'amount': amount / 100,  # Convert back to INR for display
        'currency': currency,
        'callback_url': callback_url,
    }

    return render(request, 'payment.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML
import os

from .models import Cart, Order, OrderItem, Payment
from accounts.models import User

@login_required
def cod_order(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart_view')  # No items to order

    # Calculate total price
    total_price = sum(item.product.pprice * item.quantity for item in cart_items)

    # Create Payment record
    cod_payment = Payment.objects.create(
        order_id=get_random_string(12),
        amount=total_price,
        status='COD'
    )

    # Create Order
    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        payment=cod_payment
    )
    order_items = []
    for item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.pprice,
                    total_price=item.product.pprice * item.quantity
                )
                order_items.append(order_item)

    # Save order items in the order (just in case we need to access them directly)
    order.cart_items.set(cart_items)
    order.save()

    # Clear cart
    cart_items.delete()

    # Generate invoice PDF
    items = [{
        'product_name': item.product.pname,
        'product_brand': item.product.pbrand,
        'unit_price': item.product.pprice,
        'quantity': item.quantity,
        'total': item.total_price
    } for item in cart_items]

    html_string = render_to_string('codorder.html', {
        'order': order,
        'confirmation': cod_payment,
        'items': items,
        'user': request.user,
    })

    pdf_path = os.path.join('media/pdfs', f'Order_{order.id}.pdf')
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    HTML(string=html_string).write_pdf(pdf_path)

    return redirect('orderr', payment_ids=cod_payment.id)


# --------------------- Order Confirmation (with PDF + Email) ---------------------



@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify payment signature
            client.utility.verify_payment_signature(params_dict)
            print(f"Payment Verified: {params_dict}")

            # Save payment details to database
            session_amount = request.session.get('payment_amount', 0)
            payment = Payment(order_id=order_id, payment_id=payment_id, amount=session_amount / 100, status="Success")
            payment.save()

            # ✅ Create the Order and link the payment
            cart_items = Cart.objects.filter(user=request.user)
            if not cart_items.exists():
                return render(request, 'failure.html', {'message': 'No items in cart'})

            total_price = sum(item.product.pprice * item.quantity for item in cart_items)
            print(f"Total Price: {total_price}")

            # Create the order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                payment=payment
            )

            # Debugging: Print order to verify it's created correctly
            print(f"Order Created: {order}")

            # Create OrderItem for each item in the cart and associate it with the order
            order_items = []
            for item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.pprice,
                    total_price=item.product.pprice * item.quantity
                )
                order_items.append(order_item)

                # Debugging: Print each order item to verify it's created correctly
                print(f"OrderItem Created: {order_item}")

            # Link cart items to the order (if applicable to your model)
            order.cart_items.set(cart_items)
            order.save()

            # Clear the cart after the order is placed
            cart_items.delete()

            items = [{
                'product_name': item.product.pname,
                'product_brand': item.product.pbrand,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total': item.total_price
            } for item in order_items]


                # Generate PDF invoice
            html_string = render_to_string('orderFetch.html', {
                'payment': payment,
                'order': order,
                'items': items,
                'user': request.user,
            })

            pdf_path = os.path.join('media/pdfs', f'Order_{order_id}.pdf')
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            HTML(string=html_string).write_pdf(pdf_path)

            # Send email with invoice
            subject = "Your Order Confirmation"
            body = f"Dear {request.user.get_full_name() or request.user.username},\n\nThank you for your order. Please find the invoice attached."

            email = EmailMessage(subject, body, to=[request.user.email])
            email.attach_file(pdf_path)
            email.send(fail_silently=False)
   
            return redirect('orderr', payment_ids=payment.id)

            #return render(request, 'success.html', {'payment': payment, 'order_id': payment.id, 'order_items': order_items})

        except razorpay.errors.SignatureVerificationError as e:
            print(f"Signature Verification Failed: {e}")
            return render(request, 'failure.html')
        except Exception as e:
            print(f"Payment Failed: {e}")
            return render(request, 'failure.html')

    return HttpResponseBadRequest()

# @login_required
# def confirm(request, order_id):
#     confirmation = get_object_or_404(Payment, id=order_id)

#     try:
#         order = Order.objects.get(payment=confirmation)
#         order_items = order.order_items.select_related('product')

#         items = [{
#             'product_name': item.product.pname,
#             'product_brand': item.product.pbrand,
#             'quantity': item.quantity,
#             'unit_price': item.unit_price,
#             'total': item.total_price
#         } for item in order_items]

#     except Order.DoesNotExist:
#         order = None
#         items = []

#     # Generate PDF invoice
#     html_string = render_to_string('orderFetch.html', {
#         'confirmation': confirmation,
#         'order': order,
#         'items': items,
#         'user': request.user,
#     })

#     pdf_path = os.path.join('media/pdfs', f'Order_{order_id}.pdf')
#     os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
#     HTML(string=html_string).write_pdf(pdf_path)

#     # Send email with invoice
#     subject = "Your Order Confirmation"
#     body = f"Dear {request.user.get_full_name() or request.user.username},\n\nThank you for your order. Please find the invoice attached."

#     email = EmailMessage(subject, body, to=[request.user.email])
#     email.attach_file(pdf_path)
#     email.send(fail_silently=False)

#     return redirect('orderr', order_id=order_id)


# --------------------- Order Detail View ---------------------

@login_required
def orderr(request, payment_ids):
    confirmation = get_object_or_404(Payment, id=payment_ids)

    try:
        order = Order.objects.get(payment=confirmation)
        order_items = order.order_items.select_related('product')

        items = [{
            'product_img': item.product.pimg,
            'product_name': item.product.pname,
            'product_brand': item.product.pbrand,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total': item.total_price
        } for item in order_items]

    except Order.DoesNotExist:
        order = None
        items = []

    # Fetch other delivered orders for this user
    order_history = Order.objects.filter(user=request.user, delivery_status="Delivered").exclude(id=payment_ids)

    return render(request, 'orderr.html', {
        'confirmation': confirmation,
        'order': order,
        'items': items,
        'user': request.user,
        'order_history': order_history,
    })

from django.contrib.auth.decorators import user_passes_test
# Decorator for checking if the user is admin
def admin_required(user):
    return user.is_superuser





from django.db.models import Sum
from django.shortcuts import render
from .models import OrderItem
from django.db.models.functions import TruncDate, TruncWeek, TruncYear
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import json
from datetime import timedelta

@user_passes_test(admin_required, login_url='/login/')
def sales_report(request):
    group_by = request.GET.get('group_by', 'date')  # default group by date
    export = request.GET.get('export', None)


    # Choose the truncation function and label format
    if group_by == 'week':
        trunc_func = TruncWeek('order__created_at')
        label = 'Week'
    elif group_by == 'year':
        trunc_func = TruncYear('order__created_at')
        label = 'Year'
    else:
        trunc_func = TruncDate('order__created_at')
        label = 'Date'

    # Get raw sales data grouped by time and product
    raw_data = (
        OrderItem.objects
        .filter(product__isnull=False)
        .annotate(period=trunc_func)
        .values('period', 'product__id', 'product__pname', 'product__pbrand', 'product__category')
        .annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum('total_price'),
        )
        .order_by('-period')
    )


    # Export CSV
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{group_by}.csv"'
        writer = csv.writer(response)
        writer.writerow([label, "Product ID", "Name", "Brand", "Category", "Quantity", "Total Sales"])
        for item in raw_data:
            writer.writerow([
                item['period'].strftime('%Y-%m-%d'),
                item['product__id'],
                item['product__pname'],
                item['product__pbrand'],
                item['product__category'],
                item['total_quantity'],
                float(item['total_sales']),
            ])
        return response
    # Prepare chart data by period only (aggregate total_sales per period)
    chart_dict = {}

    for item in raw_data:
        period = item['period']
        if group_by == 'year':
            period_label = period.strftime('%Y')
        elif group_by == 'week':
            start_of_week = period.strftime('%Y-%m-%d')
            end_of_week = (period + timedelta(days=6)).strftime('%Y-%m-%d')
            period_label = f'{start_of_week} to {end_of_week}'
        else:  # group_by == 'date'
            period_label = period.strftime('%Y-%m-%d')

        chart_dict[period_label] = chart_dict.get(period_label, 0) + float(item['total_sales'])

    chart_labels = list(chart_dict.keys())
    chart_values = list(chart_dict.values())

    # Optional: paginate the raw_data for the table
    from django.core.paginator import Paginator
    paginator = Paginator(raw_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'salesreport.html', {
        'sales_data': page_obj,
        'group_by': group_by,
        'label': label,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
    })