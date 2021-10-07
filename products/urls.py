from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'product_specs', views.ProductSpecViewSet)

urlpatterns = [
    path('', include(router.urls))
]