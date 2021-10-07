from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
from save_the_computer import settings


bucket = settings.INFLUXDB_BUCKET
influxdb = InfluxDBClient(
    url=f'http://{settings.INFLUXDB_HOST}:{settings.INFLUXDB_PORT}',
    token=settings.INFLUXDB_TOKEN,
    org=settings.INFLUXDB_ORG,
)

influxdb_write_api = influxdb.write_api(write_options=ASYNCHRONOUS)
influxdb_query_api = influxdb.query_api()
