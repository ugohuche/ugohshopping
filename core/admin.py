from django.contrib import admin
from .models import Item, Order, OrderItem, Address, Refund

def make_refund_accepted(modeladmin, request, queryset):
  queryset.update(refund_granted=True)
make_refund_accepted.short_description = "Update orders to refund granted"

class OrderAdmin(admin.ModelAdmin):
  list_display = [
                  'user', 
                  'ordered', 
                  'being_delivered', 
                  'recieved', 
                  'refund_requested', 
                  'refund_granted', 
                  'shipping_address',
                  'billing_address', 
                  'payment', 
                  'coupon'
                  ]
  list_display_links = [
                  'user',
                  'shipping_address',
                  'billing_address', 
                  'payment', 
                  'coupon'
                  ]
  list_filter = [
                  'ordered', 
                  'being_delivered', 
                  'recieved', 
                  'refund_requested', 
                  'refund_granted'
                  ]
  search_fields = [
                  'user__username',
                  'reference_code'
  ]
  actions = [make_refund_accepted,]

class AddressAdmin(admin.ModelAdmin):
  list_display = [
    'user',
    'street_address',
    'apartment_address',
    'country',
    'Zip',
    'address_type',
    'default'
  ]
  list_filter = ['default', 'address_type', 'country']
  search_fields = ['user', 'street_address', 'apartment_address', 'Zip']
 


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Refund)
