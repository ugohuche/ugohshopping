from django import forms


class CouponForm(forms.Form):
  code = forms.CharField(widget=forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Promo code',
    'aria-label': 'Recipient\'s username',
    'aria-describedby': 'basic-addon2'
  }))
  

class RefundForm(forms.Form):
  reference_code = forms.CharField()
  message = forms.CharField(widget=forms.Textarea(attrs={
    'rows': 4
  }))
  email = forms.EmailField()