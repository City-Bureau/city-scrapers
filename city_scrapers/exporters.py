from datetime import datetime
from pytz import timezone
from scrapy.exporters import JsonLinesItemExporter


class CityScrapersJsonLinesItemExporter(JsonLinesItemExporter):
    def serialize_field(self, field, name, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%dT%H:%M:%S')
        return super(CityScrapersJsonLinesItemExporter, self).serialize_field(field, name, value)
