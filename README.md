# 내려 가즈아 - Backend

컴퓨터 가격 차트 사이트 "내려 가즈아" 의 백엔드입니다.

<br><br>

# Docker containers
|Service|Description|port|
|-|-|-|
|MariaDB|제품의 데이터를 최신으로 유지하고 Django에게 제공하는 데이터베이스|3306|
|InfluxDB|시간에 따른 가격, 재고 상태 등 시계열 데이터를 저장하는 데이터베이스|8086|
|Django|Frontend에 json을 제공하기 위한 백엔드 서버|8241 (production: 80)|
|RabbitMQ|Celery에서 메시지 교환을 위해 사용되는 브로커|5672, 15672|
|Celery Worker|크롤링, 썸네일 다운로드 Task를 수행하는 worker||
|Celery Beat|지정된 시간 또는 일정 시간마다 Task를 생성하는 역할을 수행||

<br><br>

# Django admin 명령어

## 주의사항
```bash
$ docker-compose run django python manage.py <command>
```
Django admin은 위와 같이 docker 컨테이너에서 실행되어야 합니다.

## shell
```bash
$ docker-compose run django python manage.py shell
```

Django Shell 환경을 실행합니다. django 와 연계되는 코드를 테스트할 수 있습니다.

```python
>>> from products.tasks import collect, download_one_thumbnail
>>> download_one_thumbnail.delay()
```

위는 다운로드 대기중인 썸네일을 하나 다운로드하는 Celery task를 실행하는 코드입니다.

```python
>>> from products.models import Product
>>> Product.objects.all()
```

위는 모든 제품 목록을 가져올 수 있는 코드입니다.

```bash
$ docker-compose run django python manage.py collect
```

모든 `Product` 를 크롤링하는 Task를 실행할 수 있는 명령입니다.

**collect**: 제품 정보를 크롤링 후 저장하고 가격을 차트 데이터에 기록합니다. 이 작업은 django 내부적으로 매일 새벽 5시, 오후 5시에 실행되도록 설정되어 있습니다.

<br><br>

# Celery Task

크롤링과 썸네일 다운로드는 task 단위로 [Celery](https://docs.celeryproject.org/en/stable/) 에서 실행됩니다.

<br><br>

# Build

```bash
$ docker-compose build
```
빌드 명령은 위와 같습니다. Docker 이미지는 `solo5star/stcomputer-backend:<version>` 으로 태그됩니다.

<br><br>

# Run on development

```bash
$ docker-compose up -d
```
`docker-compose.yml` 에 정의된 서비스들을 developement 환경에서 실행하려면 위의 명령어를 입력하세요.

<br><br>

# Run on production

```bash
$ chmod +x start.production.sh
$ ./start.production.sh
```
Production 환경에서 실행하려면 `start.production.sh` 스크립트를 실행하세요. `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d` 명령의 쇼트컷입니다. Production 환경으로 실행 시 `django` 의 포트가 80으로 변경됩니다.

<br><br>

# Migration

```bash
$ docker-compose run django python manage.py migrate
```
마이그레이션은 수동으로 실행할 수 있으나 django 컨테이너 생성 시 자동으로 실행되기 때문에 별도로 실행하지 않아도 됩니다.

<br><br>

# Make Migrations

```bash
$ docker-compose run django python manage.py makemigrations
```
`Django` ORM 모델에 변경사항이 생길 시 `makemigrations` 명령을 사용하여 마이그레이션을 생성할 수 있습니다. 생성된 마이그레이션은 `migrate` 명령을 사용하여 `MariaDB` 에 반영할 수 있습니다.