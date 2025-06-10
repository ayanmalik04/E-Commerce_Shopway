from django.contrib import admin
from django.urls import path,include
from .  import views 

urlpatterns = [
   
    path('product/<int:product_id>/' , views.product_detail , name='product_detail'),
    path('cart/' , views.cart_view , name = 'cart_view'),
    path('cart/add/<int:product_id>' ,  views.add_to_cart , name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/',views.remove_from_cart, name='remove_from_cart'),
    path('orders/' , views.home , name='homes'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    #path('confirmorder/<int:order_id>/', views.confirm, name='confirmorder'),
    path('cod-order/', views.cod_order, name='cod_order'),
    #path('confirmorder1/<int:order_id>/', views.confirm, name='confirmorder1'),
    path('orderr/<int:payment_ids>/', views.orderr , name='orderr'),
    path('sales/' , views.sales_report )


    
]