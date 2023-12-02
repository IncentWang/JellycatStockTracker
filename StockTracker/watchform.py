from django import forms
from django.core.exceptions import ValidationError

def validate_url_https(value):
    if not value.startswith("https://"):
        raise ValidationError("Url should starts with \"https://\"")
    if not value.startswith("https://www.jellycat.com"):
        raise ValidationError("Url should be Offical Jellycat Store URL")

class Watchform(forms.Form):
    url = forms.CharField(label="Url of the product you want to track", max_length=200, validators=[validate_url_https])
    sku = forms.CharField(label="SKU of the product you want to track (i.e. BAH2ROS, Select colour and size first)", max_length = 10)
    email = forms.EmailField(label="Your email")
