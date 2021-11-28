from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAcceptable

from products.utils import serialize_flux_table
from .influxdb import influxdb, bucket
from .models import Product, ProductCategory, ProductSpec
from .serializers import ProductCategorySerializer, ProductSerializer, ProductSpecSerializer


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
    serializer_class = ProductSpecSerializer

    def get_queryset(self):
        # Get products by category
        query = {}
        for key in ['category_name', 'category_level1', 'category_level2']:
            if (value := self.request.query_params.get(key)) is not None:
                # category__name, category__level1, category__level2
                query[key.replace('_', '__')] = value
        
        queryset = ProductSpec.objects.filter(**query)

        # Filtering by product name
        search = self.request.query_params.get('search')
        if search is not None and len(search) > 0:
            queryset = queryset.filter(name__icontains=search)

        # sort products as registration date
        return queryset.order_by('-registration_date')


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductPriceSeries(viewsets.ViewSet):
    def extract_range_from_query(self, request):
        start = request.query_params.get('range')
        if start not in ['7d', '1mo', '6mo', '1y', '5y']:
            raise NotAcceptable(detail='range should given.')
        
        return start

    def retrieve(self, request, pk=None):
        if pk is None:
            raise NotAcceptable(detail='product_id should given.')

        start = self.extract_range_from_query(request)

        query = f'''
        from(bucket: "{bucket}")
            |> range(start: -{start}, stop: today())
            |> filter(fn: (r) => r["_measurement"] == "price")
            |> filter(fn: (r) => r["product_id"] == product_id)
            |> aggregateWindow(every: 1d, fn: last, createEmpty: true)
            |> yield(name: "last")
        '''
        query_api = influxdb.query_api()
        result = query_api.query(
            query=query,
            params={
                'product_id': pk
            })

        if len(result) == 0:
            raise NotFound()

        return Response(serialize_flux_table(result))
