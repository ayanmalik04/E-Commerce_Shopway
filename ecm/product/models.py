from django.db import models
from django.contrib.auth.models import User 
from django.conf import settings 
# Create your models here.
class productt(models.Model):
    CATEGORY_CHOICES = [
        ('Watches', 'Watches'),
        ('Shoes', 'Shoes'),
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Groceries', 'Groceries'),
       
    ]
    pimg = models.ImageField(upload_to='imagessp/' , default=False)
    pname = models.CharField(max_length=20)
    pbrand = models.CharField(max_length=20)
    pprice = models.IntegerField()
    pdesc = models.TextField(blank=True , default=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=False)

class Review(models.Model):
    product = models.ForeignKey(productt, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ FIXED
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    video = models.FileField(upload_to='review_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.pname} ({self.rating}⭐)"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(productt, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)





    
class Payment(models.Model):
    order_id = models.CharField(max_length=255, unique=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed'),  ('COD', 'Cash on Delivery') ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.status}"
    
from django.utils import timezone
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    cart_items = models.ManyToManyField(Cart)
    total_price = models.DecimalField(max_digits=20 , decimal_places=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE , null=True)
    delivery_status = models.CharField(max_length=20, default="Pending")
    is_delivered = models.BooleanField(default=False)
    is_return_requested = models.BooleanField(default=False)
    is_return_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # ✅ Add this

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(productt, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    

from django.utils.html import format_html
class SalesReport(models.Model):
    link = models.URLField( max_length=300, default= "http://127.0.0.1:8000/sales/" )

    def report(self):
        return format_html('<a href="{}" target="_blank">Open Report</a>', self.link)
    
    report.short_description = "Open Link"

    def __str__(self):
        return self.link