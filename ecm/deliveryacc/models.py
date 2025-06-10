# core/models.py or accounts/models.py


from django.db import models

REGION_CHOICES = [
    ('North Mumbai', 'North Mumbai'),
    ('South Mumbai', 'South Mumbai'),
]
class DeliveryBoyLog(models.Model):
    usernameemployee = models.CharField(max_length=200)
    passwordemployee = models.CharField(max_length=100)  # 'login', 'logout', 'order_delivered', etc.
    region = models.CharField(max_length=100 , choices=REGION_CHOICES,blank=True, null=True)

