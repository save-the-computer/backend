from django.shortcuts import render
from rest_framework import viewsets
from products.models import Product, ProductSpec
from products.serializers import ProductSerializer, ProductSpecSerializer


class ProductSpecViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductSpec.objects.all()
    serializer_class = ProductSpecSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
