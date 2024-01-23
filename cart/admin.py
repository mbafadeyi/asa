from django.contrib import admin

from .models import ColourVariation, Order, OrderItem, Product, SizeVariation

admin.site.register(ColourVariation)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(SizeVariation)
