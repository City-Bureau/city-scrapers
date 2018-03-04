# -*- coding: utf-8 -*-

from datetime import datetime
from pytz import timezone
from inflector import Inflector, English
import scrapy


class Spider(scrapy.Spider):
    inflector = Inflector(English)

    def _generate_id(self, data, start_time):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        name = self.inflector.underscore(data['name']).strip('_')
        id = data.get('id', 'x').replace('/', '-')
        try:
            start_time_str = datetime.strftime(start_time, '%Y%m%d%H%M')
        except TypeError:
            start_time_str = 'None'
        parts = [self.name, start_time_str, id, name]
        return '/'.join(parts)

    def _naive_datetime_to_tz(self, datetime_object, source_tz='America/Chicago'):
        """
        Converts a naive datetime (one without timezone information) by
        interpreting it using the source_tz.
        """
        tz = timezone(source_tz)
        return tz.localize(datetime_object)
