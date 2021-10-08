from django.shortcuts import render
from rest_framework import viewsets
from products.models import Product, ProductCategory, ProductSpec
from products.serializers import ProductCategorySerializer, ProductSerializer, ProductSpecSerializer


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    pagination_class = None

    def get_queryset(self):
        query = {}
        for key in ['name', 'level1', 'level2']:
            if (value := self.request.query_params.get(key)) is not None:
                query[key] = value

        return ProductCategory.objects.filter(**query)


class ProductSpecViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductSpec.objects.all()
    serializer_class = ProductSpecSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
