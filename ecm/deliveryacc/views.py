from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DeliveryBoyLog
# Delivery Boy Login View
def delivery_login(request):
    if request.method == 'POST':
        usernameemp = request.POST['usernameemp']
        passwordemp = request.POST['passwordemp']

        try:
            user = DeliveryBoyLog.objects.get(usernameemployee=usernameemp)

            if user.passwordemployee == passwordemp:  # Plain text comparison
                request.session['delivery_boy_id'] = user.id  # Store in session
                request.session['usernameemployee'] = user.usernameemployee  # 👈 add this

                return redirect('delivery_dashboard')
            else:
                messages.error(request, "Incorrect password.")

        except DeliveryBoyLog.DoesNotExist:
            messages.error(request, "Username does not exist.")

    return render(request, 'delivery_login.html')

# Logout View
def delivery_logout(request):
    request.session.flush()  # Clear session
    return redirect('home')

# Dashboard View
from product.models import Order  # make sure you have imported your Order model


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import Lower, Trim


def delivery_dashboard(request):
    if 'delivery_boy_id' not in request.session:
        return redirect('delivery_login')

    useremp = request.session.get('usernameemployee')
    delivery_boy = DeliveryBoyLog.objects.get(usernameemployee=useremp)

    user_region = delivery_boy.region.strip().lower()

    # Fetch all orders for users in delivery boy's region
    all_orders = Order.objects.select_related('user', 'payment') \
        .prefetch_related('order_items__product') \
        .annotate(user_region_lower=Lower(Trim('user__region'))) \
        .filter(user_region_lower=user_region) \
        .order_by('-id')

    # Separate orders into pending and return requests
    pending_orders = all_orders.exclude(delivery_status="Delivered")
    # Return requests (delivered, return requested but not yet approved)
    return_orders = all_orders.filter(
        delivery_status="Delivered",
        is_return_requested=True,
        is_return_approved=False
    )

    return render(request, 'delivery_dashboard.html', {
        'useremp': useremp,
        'pending_orders': pending_orders,
        'return_orders': return_orders
    })

def mark_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_delivered = True
    order.delivery_status = "Delivered"
    order.save()
    return redirect('delivery_dashboard')


def request_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.delivery_status == "Delivered":
        order.is_return_requested = True
        order.save()
    return redirect('orderr', order.payment.id)


def approve_return(request, order_id):
    if 'delivery_boy_id' not in request.session:
        return redirect('delivery_login')

    order = get_object_or_404(Order, id=order_id)
    if order.is_return_requested and not order.is_return_approved:
        order.is_return_approved = True
        order.save()

    return redirect('delivery_dashboard')
