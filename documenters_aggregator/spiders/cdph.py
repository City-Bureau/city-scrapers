# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

import re
from datetime import datetime
from pytz import timezone
from time import strptime


class CdphSpider(scrapy.Spider):

    name = 'cdph'
    long_name = 'Chicago Department of Public Health'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/cdph/supp_info/boh/2017-board-of-health.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        title = response.css('#content-content h1::text').extract_first()

        parts = re.match(r'(\d{4}) (.*?)s', title)
        year = int(parts.group(1))
        name = parts.group(2)

        first_paragraph = response.css('#content-content h1 + p::text').extract_first()
        description = first_paragraph.replace('The specific dates, by month, for 2017 are:', '').strip()

        for item in response.css('#content-content p'):

            text = item.css('::text').extract_first()
            matches = re.match(r'(\w+) +(\d+)', text)

            if matches is not None:
                month = int(strptime(matches.group(1), '%B').tm_mon)
                day = int(matches.group(2))
                tz = timezone('America/Chicago')

                naive_start_time = datetime(year, month, day, 9)
                start_time = tz.localize(naive_start_time).isoformat()

                naive_end_time = datetime(year, month, day, 10, 30)
                end_time = tz.localize(naive_end_time).isoformat()

                yield {
                    '_type': 'event',
                    'id': self._generate_id(start_time, name),
                    'name': name,
                    'description': description,
                    'classification': self._parse_classification(item),
                    'start_time': start_time,
                    'end_time': end_time,
                    'all_day': False,
                    'status': self._parse_status(item),
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(response)
                }

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'committee-meeting'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        A lot of this info is hard coded as it is unlikely to frequently change.
        """
        return {
            'url': 'https://www.cityofchicago.org/city/en/depts/cdph.html',
            'name': '2nd Floor Board Room, DePaul Center, 333 S. State Street, Chicago, IL',
            'coordinates': {
                'latitude': None,
                'longitude': None,
            }
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _generate_id(self, start_time, name):
        """
        We use the start time to generate an ID since there is no publically
        exposed meeting ID.
        """

        date = start_time.split('T')[0]
        dashified = re.sub(r'[^a-z]+', '-', name.lower())
        return '{0}-{1}'.format(date, dashified)

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
