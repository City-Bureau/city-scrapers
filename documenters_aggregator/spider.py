# -*- coding: utf-8 -*-
import scrapy
import re

from datetime import datetime
from pytz import timezone

from inflector import Inflector, English

class Spider(scrapy.Spider):
    inflector = Inflector(English)

    def _generate_id(self, item, data, start_time):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        name = self.inflector.underscore(data['name'])
        id = data.get('id', 'x')
        parts = [self.name, datetime.strftime(start_time, '%Y%m%d%H%M'), id, name]
        return '/'.join(parts)
