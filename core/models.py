from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField
from payments.models import Coupon, Payment 

CATEGORY_CHOICES = (
  ('S', 'Shirt'),
  ('SW', 'Sports wear'),
  ('OW', 'Outwear')
)

LABEL_CHOICES = (
  ('P', 'primary'),
  ('S', 'secondary'),
  ('D', 'danger')
)

ADDRESS_CHOICES = (
  ('B', 'Billing'),
  ('S', 'Shipping')
)



class ItemQuerySet(models.QuerySet):
  def get_shirts(self):
    return self.filter(category='S')

  def get_sportswear(self):
    return self.filter(category='SW')

  def get_outwear(self):
    return self.filter(category='OW')


class Item(models.Model):
  title = models.CharField(max_length=100)
  price = models.FloatField()
  discount_price = models.FloatField(blank=True, null=True)
  category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
  label = models.CharField(choices=LABEL_CHOICES, max_length=2)
  slug = models.SlugField()
  description = models.TextField()
  image = models.ImageField()

  objects = ItemQuerySet.as_manager()

  def __str__(self):
    return self.title

  def get_absolute_url(self):
    return reverse("products", args=[self.slug])

  def get_add_to_cart_url(self):
    return reverse("add_to_cart", args=[self.slug])

  def get_remove_from_cart_url(self):
    return reverse("remove_from_cart", args=[self.slug])



class OrderItem(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  ordered = models.BooleanField(default=False)
  quantity = models.IntegerField(default=1)

  def __str__(self):
    return f"{self.quantity} of {self.item.title}"

  def get_total_item_price(self):
    if self.item.discount_price:
      return self.quantity * self.item.discount_price
    return self.quantity * self.item.price

  def get_amount_saved(self):
    return (self.quantity * self.item.price) - (self.quantity * self.item.discount_price)



class Address(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  street_address = models.CharField(max_length=100)
  apartment_address = models.CharField(max_length=100, blank=True, null=True)
  country = CountryField(multiple=False)
  Zip = models.CharField(max_length=100)
  address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
  default = models.BooleanField(default=False)

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name_plural = 'Addresses'




class Order(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  reference_code = models.CharField(max_length=20, blank=True, null=True)
  items = models.ManyToManyField(OrderItem)
  start_date = models.DateTimeField(auto_now_add=True)
  ordered_date = models.DateTimeField()
  ordered = models.BooleanField(default=False)
  shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
  billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
  being_delivered = models.BooleanField(default=False)
  recieved = models.BooleanField(default=False)
  refund_requested = models.BooleanField(default=False)
  refund_granted = models.BooleanField(default=False)

  def __str__(self):
    return self.user.username

  def get_total(self):
    total = 0
    for order_item in self.items.all():
      total += order_item.get_total_item_price()
    if self.coupon:
      total -= self.coupon.amount
    return total


class Refund(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  reason = models.TextField()
  accepted = models.BooleanField(default=False)
  email = models.EmailField()

  def __str__(self):
    return f"{self.pk}"
