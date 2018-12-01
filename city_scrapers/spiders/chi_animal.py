# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import datetime

from dateutil.parser import parse as dateparse

from city_scrapers.constants import ADVISORY_COMMITTEE
from city_scrapers.spider import Spider


class ChiAnimalSpider(Spider):
    name = 'chi_animal'
    agency_name = 'Chicago Animal Care and Control'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.page-full-description').css("ul").css("li"):
            # Pull the string
            try:
                text = item.xpath("text()").extract()[0]
            except IndexError:
                continue

            # Strip it
            text = text.strip()

            # Pass if there's nothing left
            if not text:
                continue

            # Parse the item
            data = {
                '_type': 'event',
                'name': 'Advisory Board',
                'event_description': '',
                'classification': ADVISORY_COMMITTEE,
                'start': self._parse_start(text),
                'all_day': False,
                'location': {
                    'name': 'David R. Lee Animal Care Center',
                    'address': '2741 S. Western Ave, Chicago, IL 60608',
                },
                'sources': self._parse_sources(response),
                'documents': [],
            }
            data['id'] = self._generate_id(data)
            data['end'] = self._generate_end(data['start'])
            data['status'] = self._generate_status(data, text=text)

            yield data

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        dt = dateparse(item)
        return {
            'date': dt.date(),
            'time': dt.time(),
        }

    def _generate_end(self, start):
        """
        Estimate end date and time.
        """
        start_dt = datetime.datetime.combine(start['date'], start['time'])
        end_dt = start_dt + datetime.timedelta(hours=3)
        return {
            'date': end_dt.date(),
            'time': end_dt.time(),
            'note': 'estimated 3 hours after the start time',
        }

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
