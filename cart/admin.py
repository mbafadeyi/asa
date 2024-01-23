from django.contrib import admin

from .models import Order, OrderItem, Product

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
