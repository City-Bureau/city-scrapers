# -*- coding: utf-8 -*-
import scrapy
import re

from datetime import datetime
from pytz import timezone

class Spider(scrapy.Spider):
    def _generate_id(self, item, data, start_time):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        name = self.inflector.underscore(data['name'])
        parts = [self.name, datetime.strftime(start_time, '%Y%m%d%H%M'), 'x', name]
        return '/'.join(parts)
