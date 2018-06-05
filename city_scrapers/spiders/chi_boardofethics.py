# -*- coding: utf-8 -*-
import re
import datetime
from datetime import timedelta

import dateutil.parser

from city_scrapers.spider import Spider


class Chi_boardofethicsSpider(Spider):
    name = 'chi_boardofethics'
    long_name = 'Chicago Board of Ethics'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/ethics/supp_info/minutes.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        root = response.xpath('//h3[text() = "Meeting Schedule"]/..')
        description = root.css('p::text').extract_first()
        description = description.strip() if description else ''
        meeting_dates = root.css('tbody tr td::text').extract()
        meeting_dates = [m for m in meeting_dates if m.strip() != '']

        start_time = self._parse_time(description)
        location = self._parse_location(description)

        # Ethics board only displays are tables with all meeting dates
        # so the crawler only processes a single page that displays different
        # dates so most of the attributes are the same.
        for meeting_date in meeting_dates:
            data = {
                '_type': 'event',
                'name': 'Chicago Board of Ethics',
                'event_description': description,
                'classification': 'Board Meeting',
                'start': self._parse_start(meeting_date, start_time),
                'end': {},
                'status': 'tentative',
                'all_day': False,
                'location': location,
                'documents': [],
                'sources': [{'url': self.start_urls[0], 'note': ''}],
            }
            data['end'] = self._parse_end(data)
            data['id'] = self._generate_id(data)
            yield data

    @staticmethod
    def _parse_start(date, time):
        """
        Parse state date and time.
        """
        dt = dateutil.parser.parse('{date} {time}'.format(date=date, time=time))
        return {'date': dt.date(),
                'time': dt.time(),
                'note': ''
                }

    @staticmethod
    def _parse_end(item):
        """
        Parse end date and time.
        """

        # meeting text says approx ~2hrs so just hard coding.
        end = {}
        end['date'] = item['start']['date']
        end['note'] = item['start']['note']
        dt = datetime.datetime.combine(datetime.date(1, 1, 1), item['start']['time'])
        end['time'] = (dt + timedelta(hours=2)).time()
        return end

    @staticmethod
    def _parse_location(text):
        name = re.compile(r'(held at the) (?P<name>.*?),(?P<address>.*).')
        matches = name.search(text)
        location_name = matches.group('name').strip()
        address = matches.group('address').strip()
        return {
            'url': '',
            'name': location_name,
            'address': address,
            'neighborhood': '',
        }

    @staticmethod
    def _parse_time(text):
        time = re.compile(r'(1[0-2]|0?[1-9]):([0-5][0-9])( ?[AP]M)?')
        match = time.search(text)
        return match.group(0)
