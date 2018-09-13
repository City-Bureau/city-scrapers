# -*- coding: utf-8 -*-
import re

import scrapy
from ics import Calendar

from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class DetGreatLakesWaterAuthoritySpider(Spider):
    name = 'det_great_lakes_water_authority'
    agency_name = 'Detroit Great Lakes Water Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['www.glwater.org']
    start_urls = ['http://www.glwater.org/events/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        next_page = response.css('.tribe-events-nav-next')[0].xpath('a/@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)
        yield scrapy.Request(response.url + '?ical=1&tribe_display=month', callback=self._parse_ical)

    def _parse_ical(self, ical_event):
        cal = Calendar(ical_event.text)
        for event in cal.events:
            # Meetings parens to indicate status (e.g. (Canceled))
            desc = re.search(r'(?P<name>[^()]+)(?P<status>\(([^()]+)\))?', event.name)
            data = {
                '_type': 'event',
                'name': desc.group('name').strip(),
                'event_description': event.description,
                'classification': self._parse_classification(desc.group('name')),
                'start': {'date': event.begin.date(), 'time': event.begin.time(), 'note': ''},
                'end': {'date': event.end.date(), 'time': event.end.time(), 'note': ''},
                'all_day': event.all_day,
                'location': {'name': '', 'address': event.location, 'neighborhood': ''},
                'documents': [],
                'sources': [{'url': event.url, 'note': ''}]
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, desc.group(0))
            yield data

    @staticmethod
    def _parse_classification(name):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        if 'BOARD' in name.upper():
            return BOARD
        if 'COMMITTEE' in name.upper():
            return COMMITTEE
        return NOT_CLASSIFIED
