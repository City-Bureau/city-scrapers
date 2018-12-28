# -*- coding: utf-8 -*-
import re
from datetime import time

from dateutil.parser import parse

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class DetCityPlanningSpider(Spider):
    name = 'det_city_planning'
    agency_name = 'Detroit City Planning Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    base_url = 'https://www.detroitmi.gov/'
    start_urls = ['https://www.detroitmi.gov/Government/Boards/City-Planning-Commission-Meetings']
    location = {
        'name': 'Committee of the Whole Room, 13th floor, Coleman A. Young Municipal Center',
        'address': '2 Woodward Avenue, Detroit, MI 48226',
        'neighborhood': '',
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        dt_regex = re.compile(r'\w+\s\d+,\s\d+')
        for item in response.xpath('//tr/td/text()').extract():
            # Check if cell is actual text
            if not item[0].isalpha():
                continue
            dt_str = dt_regex.search(item).group()
            dt = parse(dt_str)
            data = {
                '_type': 'event',
                'name': 'City Planning Commission',
                'event_description': '',
                'classification': COMMISSION,
                'start': {
                    'date': dt.date(),
                    'time': time(16, 45),
                    'note': 'Meeting runs from 4:45 pm to approximately 8:00 pm'
                },
                'end': {
                    'date': dt.date(),
                    'time': time(20, 0),
                    'note': ''
                },
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(dt, response),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }]
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_documents(self, dt, response):
        """
        Parse or generate documents.
        """
        dt_str = '{}-{dt.day}-{dt.year}'.format(dt.strftime('%B').lower(), dt=dt)
        agenda_url = response.css('a[href*="{}"]::attr(href)'.format(dt_str)).extract_first()
        if agenda_url:
            return [{'url': response.urljoin(agenda_url), 'note': 'Agenda'}]
        return []
