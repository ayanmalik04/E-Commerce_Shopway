from django.urls import path
from .views import home , logg , regist , dashboard , logout_view , deletee , profile_view , update_profile , address , chatbot_view , get_answer  #custom_password_reset_complete,custom_password_reset_confirm,custom_password_reset_done,custom_password_reset_request
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', home , name = "home"),
    path('login/', logg , name = "login"),
    path('register/', regist , name = "register"),
    path('dash/', dashboard , name = "dashboard"),
    path('logout/', logout_view , name = "logout"),
    path('profile/', profile_view, name="profile"),  # ✅ Show profile
    path('delete-account/', deletee, name="delete_account"),
    path("update-profile/", update_profile, name="update_profile"),
    path('address/', address , name='update_address'),
    path('home/chatbot/', chatbot_view, name='chatbot'),
    path('get-answer/', get_answer, name='get_answer'),


    # # Custom Password Reset Views
    # path('password_reset/', custom_password_reset_request, name='password_reset'),
    # path('password_reset_done/', custom_password_reset_done, name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', custom_password_reset_confirm, name='password_reset_confirm'),
    # path('reset/done/', custom_password_reset_complete, name='password_reset_complete'),


    
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name="password_reset.html",
        email_template_name="password_reset_email.html"
    ), name='password_reset'),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name="password_reset_done.html"
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="password_reset_confirm.html"
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name="password_reset_complete.html"
    ), name='password_reset_complete'),





]