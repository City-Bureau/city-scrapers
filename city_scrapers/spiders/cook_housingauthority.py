# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import json
import urllib.parse as urlparse

import scrapy
from dateutil.parser import parse as dateparse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class CookHousingAuthoritySpider(Spider):
    name = 'cook_housingauthority'
    agency_name = 'Housing Authority of Cook County'
    allowed_domains = ['http://thehacc.org/']
    start_urls = ['http://thehacc.org/events/feed/']
    events_endpoint = 'http://thehacc.org/wp-json/tribe/events/v1/events/{id}'

    def parse(self, response):
        for url in self._gen_requests(response):
            yield scrapy.Request(
                url, callback=self._parse_event, dont_filter=True
            )

    def _gen_requests(self, response):
        for link in response.css('guid::text').extract():
            params = urlparse.parse_qs(link)
            event_id = params['p'][0]
            yield self.events_endpoint.format(id=event_id)

    def _parse_event(self, response):
        try:
            r = json.loads(response.body)
        except TypeError:
            yield {}
        else:
            event = r['json_ld']
            all_date = r['all_day']
            description = self._extract_text(r['description'])
            end_time = dateparse(event['endDate'])
            location = self._parse_location(event)
            name = event['name']
            sources = [{'note': '', 'url': event['url']}]
            start_time = dateparse(event['startDate'])
            tz = r['timezone']

            parsed_event = {
                '_type': 'event',
                'all_day': all_date,
                'classification': BOARD,
                'description': description,
                'location': location,
                'name': name,
                'sources': sources,
                'start': {
                    'date': start_time.date(),
                    'time': start_time.time(),
                    'note': '',
                },
                'end': {
                    'date': end_time.date(),
                    'time': end_time.time(),
                    'note': '',
                },
                'timezone': tz,
            }
            parsed_event['id'] = self._generate_id(parsed_event)
            parsed_event['status'] = self._generate_status(parsed_event, '')
            yield parsed_event

    def _parse_location(self, event):
        address = self._parse_address(event)
        location_name = event['location']['name']
        location = {
            'url': None,
            'address': address,
            'name': location_name,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }
        return location

    @staticmethod
    def _parse_address(event):
        address = event['location']['address']
        address = "{address}, {city} {state} {zip}".format(
            address=address['streetAddress'],
            city=address['addressLocality'],
            state=address['addressRegion'],
            zip=address['postalCode'],
        )
        return address

    @staticmethod
    def _extract_text(text):
        descs = scrapy.Selector(text=text).css('p::text').extract()
        return ' '.join([desc for desc in descs])
