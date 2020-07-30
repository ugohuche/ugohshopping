from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
  HomeView, 
  ShirtView,
  OutwearView,
  SportsWearView,
  ItemDetailView, 
  CheckoutView, 
  add_to_cart, 
  remove_from_cart, 
  SignUpView,
  OrderSummaryView,
  remove_single_item_from_cart,
  search
)

urlpatterns = [
  path('', HomeView.as_view(), name='home'),
  path('search', search, name='search'),
  path('shirts', ShirtView, name='shirts'),
  path('sports_wear', SportsWearView, name='sports_wear'),
  path('out_wear', OutwearView, name='out_wear'),
  path('products/<slug>', ItemDetailView.as_view(), name='products'),
  path('checkout', CheckoutView.as_view(), name='checkout'),
  path('order_summary', OrderSummaryView.as_view(), name='order_summary'),
  path('add_to_cart/<slug>', add_to_cart, name='add_to_cart'),
  path('remove_from_cart/<slug>', remove_from_cart, name='remove_from_cart'),
  path('remove_single_item_from_cart/<slug>', remove_single_item_from_cart, name='remove_single_item_from_cart'),
  path('login', LoginView.as_view(template_name="account/login.html"), name="account_login"),
  path('logout', LogoutView.as_view(), name="account_logout"),
  path('signup', SignUpView.as_view(), name="account_signup")
]
