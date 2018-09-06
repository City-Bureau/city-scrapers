from datetime import date, datetime, time
from scrapy.exporters import JsonLinesItemExporter


class CityScrapersJsonLinesItemExporter(JsonLinesItemExporter):
    def serialize_field(self, field, name, value):
        value = self.serialize_datetime_val(value)
        return super().serialize_field(field, name, value)

    def serialize_datetime_val(self, value):
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(value, date):
            value = value.strftime('%Y-%m-%d')
        elif isinstance(value, time):
            value = value.strftime('%H:%M:%S')
        elif isinstance(value, dict):
            value_obj = value.copy()
            for k, v in value_obj.items():
                value_obj[k] = self.serialize_datetime_val(v)
            value = value_obj
        return value
