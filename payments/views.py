from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

from .models import (
  Payment,
  Coupon
)

from core.models import ( 
  Order,
  Refund
)

from .forms import (
  CouponForm,
  RefundForm
)

import string
import random
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
  return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


@login_required  
def get_coupon(request, code):
  try:
    coupon = Coupon.objects.get(code=code)
    return coupon
  except ObjectDoesNotExist:
    messages.info(request, "This coupon those not exist")
    return redirect('checkout')



@method_decorator(login_required, name='dispatch')
class StripePaymentView(View):

  def get(self, *args, **kwargs):
    order = Order.objects.get(user=self.request.user, ordered=False)
    if order.billing_address:
      context = {
        'order': order,
        'DISPLAY_COUPON_FORM': False
      }
      return render(self.request, "payments/stripe_payment.html", context)
    else:
      messages.warning(self.request, "You do not have a billing address ")
      return redirect("checkout")

  def post(self, *args, **kwargs):
    order = Order.objects.get(user=self.request.user, ordered=False)
    token = self.request.POST.get('stripeToken') 
    amount = int(order.get_total() * 100)

    try:
      charge = stripe.Charge.create(
        amount = amount, #cents
        currency = "usd",
        source = token,
      ) 

      # create the payment
      payment = Payment()
      payment.stripe_charge_id = charge.id
      payment.user = self.request.user
      payment.amount = order.get_total()
      payment.save()

      order_items = order.items.all()
      order_items.update(ordered=True)
      for item in order_items:
        item.save()

      # assign the payment to the order
      order.ordered = True
      order.payment = payment
      order.reference_code = create_ref_code()
      order.save()

      return redirect("payment_done")

    except stripe.error.CardError as e:
      # Since it's a decline, stripe.error.CardError will be caught
      body = e.json_body
      err = body.get('error', {})
      messages.warning(self.request, f"{err.get('message')}")
      return redirect("payment_cancelled")

    except stripe.error.RateLimitError as e:
      # Too many requests made to the API too quickly
      messages.warning(self.request, "Rate limit error")
      return redirect("payment_cancelled")

    except stripe.error.InvalidRequestError as e:
      # Invalid parameters were supplied to Stripe's API
      messages.warning(self.request, "Invalid Parameters")
      return redirect("payment_cancelled")

    except stripe.error.AuthenticationError as e:
      # Authentication with Stripe's API failed
      # maybe you changed API keys recently 
      messages.warning(self.request, "Not authenticated")
      return redirect("payment_cancelled")

    except stripe.error.APIConnectionError as e:
      # Network communication with Stripe failed
      messages.warning(self.request, "Network error")
      return redirect("payment_cancelled")

    except stripe.error.StripeError as e:
      # Display a very generic error to the user ,
      # and maybe send yourself an email
      messages.warning(self.request, "Something went wrong.You were not charged. Please try again")
      return redirect("payment_cancelled")

    except Exception as e:
      # send an email to ourselves 
      messages.warning(self.request, "A serious error occured.")   
      return redirect("payment_cancelled")


@method_decorator(login_required, name='dispatch')
class AddCouponView(View):
  def post(self, *args, **kwargs):
    form = CouponForm(self.request.POST or None)
    if form.is_valid():
      try:
        code = form.cleaned_data.get('code')
        order = Order.objects.get(user= self.request.user, ordered= False)
        order.coupon = get_coupon(self.request, code)
        order.save()
        messages.success(self.request, "Successfully added coupon")
        return redirect('checkout')
      except ObjectDoesNotExist:
        messages.info(self.request, "You do not have an active order")
        return redirect('checkout')


@method_decorator(login_required, name='dispatch')
class Payment_cancelled(View):
  def get(self, *args, **kwargs):
    return render(self.request, "payments/payment_cancelled.html")


@login_required
def paypal_payment(request):
  order = get_object_or_404(Order, user=request.user, ordered=False)
  # host = request.get_host()
  order.reference_code = create_ref_code()
  order.save()
  return render(request, 'payments/paypal_payment.html', {'order': order})


@method_decorator(login_required, name='dispatch')
class Payment_done(View):
  def get(self, *args, **kwargs):
    messages.success(self.request, "Your order was successful!")
    return render(self.request, "payments/payment_done.html")

  def post(self, *args, **kwargs):
    order_qs = Order.objects.filter(user=self.request.user, ordered=False)
    if order_qs.exists():
      order = order_qs[0]
      order_items = order.items.all()
      order_items.update(ordered=True)
      for item in order_items:
        item.save()

      order.ordered = True
      order.save()
    return redirect('home')



@method_decorator(login_required, name='dispatch')
class RequestRefundView(View):
  def get(self, *args, **kwargs):
    form = RefundForm()
    context = {
      'form': form
    }
    return render(self.request, "payments/request_refund.html", context)
    
  def post(self, *args, **kwargs):
    form = RefundForm(self.request.POST)
    if form.is_valid():
      reference_code = form.cleaned_data('reference_code')
      message = form.cleaned_data('message')
      email = form.cleaned_data('email')

      try:
        order = Order.objects.get(reference_code=reference_code)
        order.refund_requested = True
        order.save()

        # store the refund
        refund = Refund()
        refund.order = order
        refund.reason = message
        refund.email = email
        refund.save()

        messages.info(self.request, "Your request was recieved.")
        return redirect('request_refund')

      except ObjectDoesNotExist:
        messages.info(self.request, "This order does not exist")
        return redirect('request_refund')