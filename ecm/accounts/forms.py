from django import forms
from .models import User

class AddressForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['address_line1', 'address_line2' , 'city', 'state', 'pincode', 'mobile' , 'region']