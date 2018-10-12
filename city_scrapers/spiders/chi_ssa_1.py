# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

from city_scrapers.spider import Spider
from city_scrapers.constants import COMMISSION


class ChiSsa1Spider(Spider):
    name = 'chi_ssa_1'
    agency_name = 'Chicago Special Service Area #1-2015'
    timezone = 'America/Chicago'
    allowed_domains = ['loopchicago.com']
    start_urls = ['https://loopchicago.com/about-state-street-ssa1-2015/state-street-commission/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = self._parse_location(response)
        for item in response.css('.layoutArea li'):
            data = {
                '_type': 'event',
                'name': 'State Street Commission',
                'event_description': '',
                'classification': COMMISSION,
                'start': self._parse_start(item),
                'all_day': False,
                'location': location,
                'documents': self._parse_documents(item),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['end'] = {
                'date': data['start']['date'],
                'time': None,
                'note': '',
            }
            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)
            yield data

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date_str = item.css('*::text').extract_first()
        date_match = re.search(r'\w{3,9} \d{1,2}, \d{4}', date_str)
        if date_match:
            parsed_date = datetime.strptime(date_match.group(), '%B %d, %Y')
            return {
                'date': parsed_date.date(),
                'time': time(14, 0),
                'note': '',
            }

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        if '190 N. State St.' in response.text:
            return {
                'address': '190 N State St Chicago, IL 60601',
                'name': 'ABC 7 Chicago',
                'neighborhood': '',
            }
        else:
            raise ValueError('Meeting address has changed')

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        item_link = item.css('a::attr(href)').extract_first()
        if item_link:
            return [{
                'url': 'https://loopchicago.com{}'.format(item_link),
                'note': 'Minutes'
            }]
        return []
