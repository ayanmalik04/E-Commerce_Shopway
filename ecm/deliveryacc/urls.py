from django.contrib import admin
from django.urls import path,include
from . import views 

urlpatterns = [
  path('delivery/emplogin/', views.delivery_login, name='delivery_login'),
    path('delivery/emplogout/', views.delivery_logout, name='delivery_logout'),
    path('delivery/empdashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('mark-delivered/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    path('order/<int:order_id>/return/', views.request_return, name='request_return'),
    path('order/<int:order_id>/approve-return/', views.approve_return, name='approve_return'),


]