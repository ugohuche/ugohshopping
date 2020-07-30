from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from .models import (
  Item, 
  Order, 
  OrderItem, 
  Address
)

from .forms import CheckoutForm
from payments.forms import CouponForm
from payments.models import Coupon



def is_valid_form(values):
  valid = True
  for field in values:
    if field == '':
      valid = False
  return valid


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
  def get(self, *args, **kwargs):
    try:
      order = Order.objects.get(user=self.request.user, ordered=False)
      # form
      form = CheckoutForm()
      context = {
        'form': form,
        'couponform': CouponForm(),
        'order': order,
        'DISPLAY_COUPON_FORM': True
      }

      shipping_address_qs = Address.objects.filter(
        user=self.request.user,
        address_type='S',
        default=True
      )
      if shipping_address_qs.exists():
        context.update({'default_shipping_address': shipping_address_qs[0]})

      billing_address_qs = Address.objects.filter(
        user=self.request.user,
        address_type='B',
        default=True
      )
      if billing_address_qs.exists():
        context.update({'default_billing_address': billing_address_qs[0]})

      return render (self.request, "core/checkout.html", context)
    except ObjectDoesNotExist:
      messages.info(self.request, "You do not have an active order")
      return redirect('checkout')

  def post(self, *args, **kwargs):
    form = CheckoutForm(self.request.POST or None) 
    try:
      order = Order.objects.get(user=self.request.user, ordered=False)
      if form.is_valid():
        print("Form is valid")
      
      if True:
        # Logic to use the default shipping address during checkout 
        use_default_shipping = form.cleaned_data.get('use_default_shipping')
        if use_default_shipping:
          print("Using default shipping")
          address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='S',
            default=True
          )
          if address_qs.exists():
            shipping_address = address_qs[0]
            order.shipping_address = shipping_address
            order.save()
          else:
            messages.info(self.request, "No default shipping address available")
            return redirect('checkout')
        else:
          print('User is now entering a new shipping address')
          shipping_address_1 = form.cleaned_data.get('shipping_address')
          shipping_address_2 = form.cleaned_data.get('shipping_address_2')
          shipping_country = form.cleaned_data.get('shipping_country')
          shipping_zip = form.cleaned_data.get('shipping_zip')

          if is_valid_form([shipping_address_1, shipping_country, shipping_zip]):
            shipping_address = Address(
              user=self.request.user,
              street_address=shipping_address_1,
              apartment_address=shipping_address_2,
              country=shipping_country,
              Zip=shipping_zip,
              address_type='S'
            )
            shipping_address.save()

            order.shipping_address = shipping_address
            order.save()

            # logic to set shipping address as default
            set_default_shipping = form.cleaned_data.get('set_default_shipping')
            if set_default_shipping:
              shipping_address.default = True
              shipping_address.save()

          else:
            messages.info(self.request, "Please fill in the required shipping address fields")
            return redirect('checkout')

        same_billing_address = form.cleaned_data.get('same_billing_address')
        use_default_billing = form.cleaned_data.get('use_default_billing')
        if same_billing_address:
          billing_address = shipping_address
          billing_address.pk = None
          billing_address.address_type = 'B'
          billing_address.save()
          order.billing_address = billing_address
          order.save()


        # Logic to use the default billing address 
        elif use_default_billing:
          print("Using default billing")
          address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='B',
            default=True
          )
          if address_qs.exists():
            billing_address = address_qs[0]
            order.billing_address = billing_address
            order.save()
          else:
            messages.info(self.request, "No default billing address available")
            return redirect('checkout')
        else:
          print('User is now entering a new billing address')
          billing_address_1 = form.cleaned_data.get('billing_address')
          billing_address_2 = form.cleaned_data.get('billing_address_2')
          billing_country = form.cleaned_data.get('billing_country')
          billing_zip = form.cleaned_data.get('billing_zip')

          if is_valid_form([billing_address_1, billing_country, billing_zip]):
            billing_address = Address(
              user=self.request.user,
              street_address=billing_address_1,
              apartment_address=billing_address_2,
              country=billing_country,
              Zip=billing_zip,
              address_type='B'
            )
            billing_address.save()

            order.billing_address = billing_address
            order.save()

            # logic to set billing address as default
            set_default_billing = form.cleaned_data.get('set_default_billing')
            if set_default_billing:
              billing_address.default = True
              billing_address.save()
              
          else:
            messages.info(self.request, "Please fill in the required billing address fields")
            return redirect('checkout')


        payment_option = form.cleaned_data.get('payment_option')

        if payment_option == 'S':
          return redirect("stripe_payment")
        elif payment_option == 'P':
          return redirect("paypal_payment")
        else:
          messages.warning(self.request, "Invalid payment option selected")
          return redirect("checkout")
      else:
        messages.warning(self.request, "Please fill the form correctly")
        return redirect("checkout")
      
    except ObjectDoesNotExist:
      messages.warning(self.request, "You do not have an active order")
      return redirect("order_summary")




@login_required
def search(request):
  if request.method == "POST":
    query = request.POST['Search']
    item = Item.objects.filter(title=query)
    if len(item) > 0:
      if item[0].category == 'S':
        return render(request, 'core/shirt.html', {'Shirts': item})

      elif item[0].category == 'OW':
        return render(request, 'core/outwear.html', {'Outwears': item})

      elif item[0].category == 'SW':
        return render(request, 'core/sportswear.html', {'Sportswear': item})

    else:
      messages.info(request, "Item not found")
      return redirect('home')



class HomeView(ListView):
  model = Item
  paginate_by = 10
  template_name = "core/home.html"

def ShirtView(request):
  Shirts = Item.objects.get_shirts()
  return render(request, "core/shirt.html", {'Shirts': Shirts})

def SportsWearView(request):
  Sportswear = Item.objects.get_sportswear()
  return render(request, "core/sportswear.html", {'Sportswear': Sportswear})

def OutwearView(request):
  Outwears = Item.objects.get_outwear()
  return render(request, "core/outwear.html", {'Outwears': Outwears })



@method_decorator(login_required, name='dispatch')
class OrderSummaryView(View):
  def get(self, *args, **kwargs):
    try:
      order = Order.objects.get(user=self.request.user, ordered=False)
    except ObjectDoesNotExist:
      messages.warning(self.request, "You do not have an active ordeer")
      return redirect("/")
    context = {
      'object': order
    }
    return render(self.request, "core/order_summary.html", context)


@method_decorator(login_required, name='dispatch')
class ItemDetailView(DetailView):
  model = Item
  template_name = "core/products.html"



@login_required
def add_to_cart(request, slug):
  item = get_object_or_404(Item, slug=slug)
  order_item, created = OrderItem.objects.get_or_create(
    item=item, 
    user=request.user, 
    ordered=False
  )
  order_qs = Order.objects.filter(user=request.user, ordered=False)
  if order_qs.exists():
    order = order_qs[0]
    # check if the order item is in the order
    if order.items.filter(item__slug=item.slug).exists():
      order_item.quantity += 1
      order_item.save()
      messages.info(request, "This item quantity was updated in your cart")
    else:
      messages.info(request, "This item was added to your cart")
      order.items.add(order_item)
  else:
    ordered_date = timezone.now()
    order = Order.objects.create(user=request.user, ordered_date=ordered_date)
    order.items.add(order_item)
    messages.info(request, "This item was added to your cart")
  return redirect('order_summary')


@login_required
def remove_from_cart(request, slug):
  item = get_object_or_404(Item, slug=slug)
  order_qs = Order.objects.filter(user=request.user, ordered=False)
  if order_qs.exists():
    order = order_qs[0]
    # check if the order item is in the order
    if order.items.filter(item__slug=item.slug).exists():
      order_item = OrderItem.objects.filter(
        item=item, 
        user=request.user, 
        ordered=False
      )[0]
      order_item.delete()
      messages.info(request, "This item was removed from your cart")
      return redirect('order_summary')
    else:
      messages.info(request, "This item was not in your cart")
      return redirect('products', slug)
  else:
    messages.info(request, "You do not have an active order")
    return redirect('products', slug)
  
class SignUpView(CreateView):
  form_class = UserCreationForm
  template_name = "account/signup.html"
  success_url = reverse_lazy('home')



@login_required
def remove_single_item_from_cart(request, slug):
  item = get_object_or_404(Item, slug=slug)
  order_qs = Order.objects.filter(user=request.user, ordered=False)
  if order_qs.exists():
    order = order_qs[0]
    # check if the order item is in the order
    if order.items.filter(item__slug=item.slug).exists():
      order_item = OrderItem.objects.filter(
        item=item, 
        user=request.user, 
        ordered=False
      )[0]
      if order_item.quantity == 1:
        order_item.delete()
      else:
        order_item.quantity -= 1
        order_item.save()
      messages.info(request, "This item quantity was updated") 
      return redirect('order_summary')
    else:
      messages.info(request, "This item was not in your cart")
      return redirect('products', slug)
  else:
    messages.info(request, "You do not have an active order")
    return redirect('products', slug)
  


