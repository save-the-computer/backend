from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    level1 = models.CharField(max_length=100)
    level2 = models.CharField(max_length=100)

    class Meta:
        unique_together = (('name', 'level1', 'level2'),)


class ProductSpec(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='thumbnails')
    registration_date = models.DateField()
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    variant = models.CharField(max_length=200)
    price = models.IntegerField(null=True)
    stock_state = models.CharField(max_length=30)
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.CASCADE, related_name='products', null=False)
    updated_at = models.DateTimeField(auto_now=True)


class WritePointQueuedProduct(models.Model):
    id = models.OneToOneField(Product, on_delete=models.CASCADE, null=False, primary_key=True)


class DownloadThumbnailQueuedProductSpec(models.Model):
    id = models.OneToOneField(ProductSpec, on_delete=models.CASCADE, null=False, primary_key=True)
    thumbnail_url = models.URLField()