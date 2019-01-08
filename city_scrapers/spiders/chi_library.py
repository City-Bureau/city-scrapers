# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import datetime
import re

import requests

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiLibrarySpider(Spider):
    name = 'chi_library'
    agency_name = 'Chicago Public Library'
    timezone = 'America/Chicago'
    allowed_domains = ['https://www.chipublib.org/']
    start_urls = ['https://www.chipublib.org/board-of-directors/board-meeting-schedule/']

    def __init__(self, *args, session=requests.Session(), **kwargs):
        """
        Initialize a spider with a session object to use for determining whether documents exist
        """
        super().__init__(*args, **kwargs)
        self.session = session

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        year = response.css('div.entry-content h2::text').extract_first()
        for item in response.css('div.entry-content p'):
            if len(item.css('strong')) == 0:
                continue
            start_time = self._parse_start(item, year)
            data = {
                '_type': 'event',
                'name': 'Board of Directors',
                'description': '',
                'classification': BOARD,
                'start': {
                    'date': start_time.date(),
                    'time': start_time.time(),
                    'note': '',
                },
                'end': {
                    'date': None,
                    'time': None,
                    'note': '',
                },
                'all_day': False,
                'location': self._parse_location(item),
                'documents': self._parse_documents(start_time),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data)
            yield data

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        addr_str = '{} Chicago, IL'.format(item.css('::text')[-1].extract().strip())
        return {
            'name': item.css('a::text').extract_first(),
            'address': addr_str,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_start(self, item, year):
        """
        Parse start date and time.
        """
        dt_str = item.css('strong::text').extract_first()
        return datetime.datetime.strptime(
            '{} {}'.format(re.sub(r'[,\.]', '', dt_str), year), '%A %B %d %I %p %Y'
        )

    def _parse_documents(self, start_time):
        """Check if agenda and minutes are valid URLs, add to documents if so"""
        agenda_url = (
            'https://www.chipublib.org/news/board-of-directors-'
            'meeting-agenda-{}-{date.day}-{date.year}/'
        ).format(
            start_time.strftime('%B').lower(),
            date=start_time,
        )
        minutes_url = agenda_url.replace('agenda', 'minutes')
        agenda_res = self.session.get(agenda_url)
        minutes_res = self.session.get(minutes_url)
        documents = []
        if agenda_res.status_code == 200:
            documents.append({
                'url': agenda_url,
                'note': 'Agenda',
            })
        if minutes_res.status_code == 200:
            documents.append({
                'url': minutes_url,
                'note': 'Minutes',
            })
        return documents

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
