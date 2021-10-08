from rest_framework import serializers

from products.models import Product, ProductCategory, ProductSpec


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSpecSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = ProductSpec
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'