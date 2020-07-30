from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
  paypal_payment,
  Payment_done,
  Payment_cancelled,
  StripePaymentView,
  RequestRefundView,
  AddCouponView
)


urlpatterns = [
  path('paypal', paypal_payment, name="paypal_payment"),
  path('add_coupon', AddCouponView.as_view(), name='add_coupon'),
  path('payment_done', Payment_done.as_view(), name="payment_done"),
  path('payment_cancelled', Payment_cancelled.as_view(), name="payment_cancelled"),
  path('stripe', StripePaymentView.as_view(), name="stripe_payment"),
  path('request_refund', RequestRefundView.as_view(), name="request_refund")
]