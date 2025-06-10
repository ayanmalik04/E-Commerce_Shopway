from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

REGION_CHOICES = [
    ('North Mumbai', 'North Mumbai'),
    ('South Mumbai', 'South Mumbai'),
]

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True )
    address_line1 = models.CharField(max_length=100,blank=True,null=True)
    address_line2 = models.CharField(max_length=100,blank=True,null=True)
    city = models.CharField(max_length=100,blank=True,null=True)
    state = models.CharField(max_length=100,blank=True,null=True)
    pincode = models.IntegerField(blank=True,null=True)
    mobile = models.IntegerField(blank=True,null=True)
    region = models.CharField(max_length=100,choices=REGION_CHOICES, blank=True, null=True)
    
    USERNAME_FIELD = "username" 
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]  

    def __str__(self):
        return self.username


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


