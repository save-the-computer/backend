from django.contrib import admin
from .models import Product, ProductCategory, ProductSpec


admin.site.register(ProductCategory)
admin.site.register(ProductSpec)
admin.site.register(Product)