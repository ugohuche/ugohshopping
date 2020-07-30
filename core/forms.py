from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
  ('S', 'Stripe'),
  ('P', 'Paypal')
)
class CheckoutForm(forms.Form):
  shipping_address = forms.CharField(required=False)
  shipping_address_2 = forms.CharField() 
  shipping_country = CountryField(blank_label='(select country)').formfield(
    required=False,
    widget=CountrySelectWidget(attrs={
    'class':"custom-select d-block w-100"
  }))
  shipping_zip = forms.CharField(required=False)

  billing_address = forms.CharField(required=False)
  billing_address_2 = forms.CharField() 
  billing_country = CountryField(blank_label='(select country)').formfield(
    required=False,
    widget=CountrySelectWidget(attrs={
    'class':"custom-select d-block w-100"
  }))
  billing_zip = forms.CharField(required=False)

  same_billing_address = forms.BooleanField()
  set_default_shipping = forms.BooleanField()
  use_default_shipping = forms.BooleanField()
  set_default_billing = forms.BooleanField()
  use_default_billing = forms.BooleanField()
  
  payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES, required=True)

