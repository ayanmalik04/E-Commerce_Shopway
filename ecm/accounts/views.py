from django.http import HttpResponse
from django.shortcuts import render , redirect
from .models import User , ContactMessage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.contrib import messages
from product.models import productt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model  
from django.db import connection
User = get_user_model()  


import time
from difflib import get_close_matches
from django.http import JsonResponse
from django.shortcuts import render

# Lowercased QA dictionary for fuzzy matching
qa_pairs = {
    "what are your business hours?": "Our business hours are 9 AM to 6 PM, Monday to Friday.",
    "how can i track my order?": "You can track your order by visiting the order tracking page.",
    "do you offer free shipping?": "Yes, we offer free shipping on orders over $50.",
    "what is your return policy?": "We offer a 30-day return policy on all items.",
    "hii": "Hello",
    "bye": "Have a Nice Day"
}

def chatbot_view(request):
    questions = list(qa_pairs.keys())
    return render(request, 'home.html', {'questions': questions})

def get_answer(request):
    question = request.GET.get('question', '').strip().lower()  # Normalize input

    if question:
        time.sleep(1.5)  # Simulate typing delay

        # Fuzzy matching with lower threshold (70% similarity)
        matches = get_close_matches(question, qa_pairs.keys(), n=1, cutoff=0.6)

        if matches:
            answer = qa_pairs[matches[0]]
        else:
            answer = "Sorry, I don't understand that question."

        return JsonResponse({'answer': answer})
    else:
        return JsonResponse({'answer': "No question provided."})






from product.models import Order

def home(request):
    order = None
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST["email"]
        message = request.POST["message"]
        
        ContactMessage.objects.create(name=name, email=email, message=message)

        subject = f"New Message from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        send_mail(subject, body, "mdayaanparvez@gmail.com", ["mdayaanparvez@gmail.com" , "s99687831@gmail.com"])

        messages.success(request, "Your message has been sent and saved!")
         # Ensure that the order is retrieved even for GET requests
    
    # Ensure that the most recent order is retrieved even for GET requests
    # Fetch the most recent order based on the Payment's created_at field
    # Ensure the user is logged in
       # ✅ Fetch the most recent order if user is authenticated
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-id').first()
    return render(request, 'home.html' , {'order': order} )

def logg(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Trying login with username: {username}, password: {password}")

        user = authenticate(request, username=username, password=password)
        print(f"Authenticate returned: {user}")
        if user is not None:
            login(request, user)
            print("User authenticated:", request.user.is_authenticated)   
            return redirect("dashboard")  
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html" )
from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import redirect

def regist(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

      
        if User.objects.filter(username=username).exists():
            return render(request, "reg.html", {"error": "Username already taken"})
        
        if User.objects.filter(email=email).exists():
            return render(request, "reg.html", {"error": "Email already exists"})

        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()

        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            
            return redirect("dashboard") 
        else:
            return render(request, "reg.html", {"error": "Authentication failed"})

    return render(request, "reg.html")




@login_required(login_url="login")
def dashboard(request):
    order = None
    username = request.user.username
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")

    # Base queryset
    p = productt.objects.all()

    # Apply filters
    if query:
        p = p.filter(Q(pname__icontains=query) | Q(pbrand__icontains=query))
    if category:
        p = p.filter(category=category)


    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-id').first()

    return render(request, "dashboard.html", {
        "username": username,
        "p": p,
        "query": query,
        "selected_category": category,
        'order': order
    })

def logout_view(request):
    logout(request) 
    request.session.flush()  
    connection.close()  # Closes the database connection (Fix for SQLite)
    return redirect("login") 

@login_required(login_url="login")
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})

@login_required(login_url="login")
def deletee(request):
    if request.method == "POST":
        request.user.delete()
        logout(request) 
        return redirect("home") 

    return redirect("profile")  

@login_required(login_url="login")
def update_profile(request):
    user = request.user

    if request.method == "POST":
        new_name = request.POST.get("username")
        new_password = request.POST.get("password")

        if new_name:
            user.username = new_name  
        
        if new_password:
            user.set_password(new_password)  
        user.save()
        messages.success(request, "Profile updated successfully!")

        return redirect("profile") 
    

    return render(request, "update_profile.html", {"user": user})




from .forms import AddressForm 
@login_required
def address(request):
    user = request.user
    if request.method == 'POST':
        form = AddressForm(request.POST, instance = user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AddressForm(instance=user)
    return render(request, 'address.html' , {'form': form})


# from django.shortcuts import render, redirect
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.template.loader import render_to_string
# from django.core.mail import send_mail
# from django.contrib.auth import get_user_model
# from django.conf import settings

# User = get_user_model()

# def custom_password_reset_request(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         user = User.objects.filter(email=email).first()
#         if user:
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             reset_link = request.build_absolute_uri(f'/reset/{uid}/{token}/')

#             message = render_to_string('password_reset_email.html', {
#                 'user': user,
#                 'reset_link': reset_link,
#             })

#             send_mail(
#                 'Password Reset',
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [email],
#                 fail_silently=False
#             )

#         return redirect('password_reset_done')

#     return render(request, 'password_reset.html')



# def custom_password_reset_done(request):
#     return render(request, 'password_reset_done.html')


# from django.contrib.auth.tokens import default_token_generator
# from django.contrib import messages
# from django.contrib.auth import login as auth_login

# def custom_password_reset_confirm(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (User.DoesNotExist, ValueError, TypeError):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):
#         if request.method == 'POST':
#             password1 = request.POST.get('new_password1')
#             password2 = request.POST.get('new_password2')

#             if password1 and password1 == password2:
#                 user.set_password(password1)
#                 user.save()
#                 print("New hashed password:", user.password)
#                 return redirect('password_reset_complete')
#             else:
#                 messages.error(request, "Passwords do not match.")
#         return render(request, 'password_reset_confirm.html', {'validlink': True})
#     else:
#         return render(request, 'password_reset_confirm.html', {'validlink': False})



# def custom_password_reset_complete(request):
#     return render(request, 'password_reset_complete.html')



