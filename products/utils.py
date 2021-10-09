import random
import time
import json
from typing import List
from influxdb_client.client.flux_table import FluxStructureEncoder, FluxTable


class Pseudo:
    def sleep(self, min_seconds: int):
        weight = 2.5
        bias = random.random() * min_seconds * weight
        time.sleep(min_seconds + bias)


pseudo = Pseudo()


def serialize_flux_table(tables: List[FluxTable]):
    serialized = {}
    serialized['start'] = tables[0].records[0].values['_time']
    serialized['end'] = tables[0].records[-1].values['_time']
    serialized['series'] = {}

    for table in tables:
        series = []

        for row in table.records:
            values = row.values
            series.append(values['_value'])

        field = table.records[0].values['_field']
        serialized['series'][field] = series
    
    return serialized