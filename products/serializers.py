from rest_framework import serializers

from products.models import Product, ProductCategory, ProductSpec


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductSpecSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ProductSpec
        fields = '__all__'
        extra_fields = ['products']
    
    def get_field_names(self, declared_fields, info):
        return super(ProductSpecSerializer, self).get_field_names(declared_fields, info) + self.Meta.extra_fields