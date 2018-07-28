# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
import json
from dateutil.parser import parse as dateparse


class DetLandBankSpider(Spider):
    name = 'det_land_bank'
    agency_id = 'Detroit Land Bank Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['buildingdetroit.org']
    start_urls = ['https://buildingdetroit.org/events/meetings']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        data = response.xpath('substring-before(substring-after(//script[contains(text(), "var meeting =")]/text(), "var meeting ="), ";")').extract()[0]
        entries = json.loads(data)

        for item in entries:

            data = {
                '_type': 'event',
                'name': item['title_tmp'],
                'event_description': item['content'],
                'classification': self._parse_classification(item),
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': self._parse_location(item),
                'documents': self._parse_documents(item),
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        if 'board of director' in item['category_type'].lower():
            return 'Board'
        return 'Committee'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        dt = dateparse(item['start'])
        return {'date': dt.date(), 'time': dt.time(), 'note': ''}

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': item['address'] + " " + item['city'] + ", " + item['state'] + " " + item['zipcode'],
            'name': '',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        if item['file_path']:
            return [{'url': item['file_path'], 'note': 'minutes'}]
        return []
