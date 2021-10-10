from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'categories', views.ProductCategoryViewSet, basename='ProductCategory')
router.register(r'products', views.ProductViewSet)
router.register(r'product_specs', views.ProductSpecViewSet, basename='ProductSpec')
router.register(r'product_price_series', views.ProductPriceSeries, basename='ProductPriceSeries')

urlpatterns = [
    path('', include(router.urls)),
]