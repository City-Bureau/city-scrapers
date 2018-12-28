# -*- coding: utf-8 -*-
from datetime import time

from dateutil.parser import parse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class DetZoningAppealsSpider(Spider):
    name = 'det_zoning_appeals'
    agency_name = 'Detroit Zoning Division'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['https://www.detroitmi.gov/Government/Boards/Board-of-Zoning-Appeals-Meeting']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {
            'name': '13th Floor in the Auditorium, Coleman A. Young Municipal Center',
            'address': '2 Woodward Avenue, Detroit, MI 48226',
            'neighborhood': '',
        }
        for item in response.css('.field td::text').extract():
            if not item.strip():
                continue
            start = self._parse_start(item)
            data = {
                '_type': 'event',
                'name': 'Board of Zoning Appeals',
                'event_description': '',
                'classification': BOARD,
                'start': start,
                'end': {
                    'date': start['date'],
                    'time': None,
                    'note': ''
                },
                'all_day': False,
                'location': location,
                'documents': self._parse_documents(start['date'], response),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }],
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        return {
            'date': parse(item).date(),
            'time': time(9, 0),
            'note': '',
        }

    def _parse_documents(self, dt, response):
        """
        Parse or generate documents.
        """
        dt_str = '{}-{dt.day}-{dt.year}'.format(dt.strftime('%B').lower(), dt=dt)
        minutes_url = response.css('a[href*="{}"]::attr(href)'.format(dt_str)).extract_first()
        if minutes_url:
            return [{'url': response.urljoin(minutes_url), 'note': 'Minutes'}]
        return []
