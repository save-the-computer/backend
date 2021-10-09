from celery import chain
from celery.app import shared_task
import requests
from influxdb_client.client.write.point import Point
from stcomputer_collector.collectors import get_collector
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
from .models import DownloadThumbnailQueuedProductSpec, ProductCategory, Product, ProductSpec, WritePointQueuedProduct
from .influxdb import influxdb, bucket
from .utils import pseudo


@shared_task
def collect():
    tasks = [collect_products.si(collector_conf['collector'], collector_conf['page_limit']) for collector_conf in settings.STCOMPUTER_COLLECTORS]
    tasks.append(write_points.si())

    tasks_chain = chain(tasks)
    tasks_chain()


@shared_task
def collect_products(collector_name: str, page_limit: int):
    raw_product_specs = []

    # Collect data using API
    for batch_raw_product_specs in get_collector(collector_name).collect(page_limit):
        raw_product_specs += batch_raw_product_specs

        # Throttle each request for 20 seconds
        pseudo.sleep(20)

    print(f'{collector_name} collects {len(raw_product_specs)} product specs.')

    # array for batch create or update
    batch_create_product_specs = []
    batch_update_product_specs = []
    batch_create_products = []
    batch_update_products = []
    batch_create_dtq_product_specs = []

    # Get all ProductSpec
    product_spec_ids = [*map(lambda product_spec: product_spec.id, raw_product_specs)]
    product_specs_by_id = ProductSpec.objects.in_bulk(product_spec_ids)

    # Get all Product     
    product_ids = []
    for raw_product_spec in raw_product_specs:
        for raw_product in raw_product_spec.products:
            product_ids.append(raw_product.id)

    product_by_id = Product.objects.in_bulk(product_ids)

    # Get all DownloadThumbnailQueuedProduct
    dtq_product_specs_by_id = DownloadThumbnailQueuedProductSpec.objects.in_bulk(product_spec_ids)

    # Iterate products
    for raw_product_spec in raw_product_specs:
        # get category
        product_category, created = ProductCategory.objects.get_or_create(
            name=raw_product_spec.classification.category,
            level1=raw_product_spec.classification.level1,
            level2=raw_product_spec.classification.level2,
        )

        product_spec = product_specs_by_id.get(raw_product_spec.id, None)

        if product_spec is None:
            product_spec = ProductSpec(
                id=raw_product_spec.id,
                name=raw_product_spec.name,
                registration_date=raw_product_spec.registration_date,
                category=product_category,
            )
            batch_create_product_specs.append(product_spec)
        else:
            product_spec.name = raw_product_spec.name
            product_spec.registration_date = raw_product_spec.registration_date
            product_spec.category = product_category
            batch_update_product_specs.append(product_spec)

        # 1) if thumbnail image is null, add to DownloadThumbnailQueuedProduct
        # 2) check already download queued
        if not product_spec.thumbnail and product_spec.id not in dtq_product_specs_by_id:
            # add to dtq_products
            batch_create_dtq_product_specs.append(DownloadThumbnailQueuedProductSpec(
                id=product_spec,
                thumbnail_url=raw_product_spec.thumbnail,
            ))

        # iterate products under product specs
        for raw_product in raw_product_spec.products:
            product = product_by_id.get(raw_product.id, None)
            
            if product is None:
                product = Product(
                    id=raw_product.id,
                    variant=raw_product.variant,
                    price=raw_product.price,
                    stock_state=raw_product.stock_state,
                    product_spec=product_spec,
                )
                batch_create_products.append(product)
            else:
                product.variant = raw_product.variant
                product.price = raw_product.price
                product.stock_state = raw_product.stock_state
                product.product_spec = product_spec
                batch_update_products.append(product)

    # Bulk update or create data
    ProductSpec.objects.bulk_create(batch_create_product_specs)
    ProductSpec.objects.bulk_update(batch_update_product_specs, fields=['name', 'registration_date', 'category'])
    Product.objects.bulk_create(batch_create_products)
    Product.objects.bulk_update(batch_update_products, fields=['variant', 'price', 'stock_state', 'product_spec'])

    print(f'{len(batch_create_product_specs)} of product specs created.')
    print(f'{len(batch_update_product_specs)} of product specs updated.')
    print(f'{len(batch_create_products)} of products created.')
    print(f'{len(batch_update_products)} of products updated.')

    # Add to queue (will writed on write_points)
    WritePointQueuedProduct.objects.bulk_create(
        [WritePointQueuedProduct(id=product) for product in batch_create_products + batch_update_products],
        ignore_conflicts=True
    )

    # Add to queue (will download thumbnail on download_one_thumbnail)
    DownloadThumbnailQueuedProductSpec.objects.bulk_create(
        batch_create_dtq_product_specs,
        ignore_conflicts=True
    )

    print(f'{len(batch_create_dtq_product_specs)} of thumbnails download queued')

    # Throttle
    pseudo.sleep(20)



@shared_task
def write_points():
    """
    InfluxDB에 가격 데이터를 기록하는 task.
    collect task가 실행된 후 실행되어야 하며, 반드시 하루에 한 번 실행되어야 함
    """
    # with 문을 사용함으로써 배치 처리를 할 수 있음.
    count = 0
    with influxdb.write_api() as write_api:
        for product in WritePointQueuedProduct.objects.all():
            product = product.id # id is foreign key of Product. so product.id is Product object
            point = Point('price') \
                .tag('product_id', product.id) \
                .tag('product_spec_id', product.product_spec.id) \
                .tag('category_name', product.product_spec.category.name) \
                .tag('category_level1', product.product_spec.category.level1) \
                .tag('category_level2', product.product_spec.category.level2) \
                .tag('variant', product.variant) \
                .field('price', product.price) \
                .field('stock_state', product.stock_state)

            write_api.write(bucket=bucket, record=point)
            count += 1
    
    WritePointQueuedProduct.objects.all().delete()
    print(f'{count} of points writed')


@shared_task
def download_one_thumbnail():
    """
    다운로드 대기중인 썸네일 중 하나를 다운로드한다.
    """
    dtq_product_spec = DownloadThumbnailQueuedProductSpec.objects.order_by('-id').first()

    if dtq_product_spec is None:
        print(f'Nothing to download, terminate.')
        return

    temp_file = NamedTemporaryFile(delete=True)

    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
    }
    response = session.get(dtq_product_spec.thumbnail_url)
    temp_file.write(response.content)
    temp_file.flush()

    dtq_product_spec.id.thumbnail.save(
        f'{dtq_product_spec.id.id}',
        File(temp_file)
    )
    dtq_product_spec.delete()