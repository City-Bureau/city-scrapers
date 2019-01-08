# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

import scrapy

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiSsa42Spider(Spider):
    name = 'chi_ssa_42'
    agency_name = 'Chicago Special Service Area #42 71st St/Stony Island'
    timezone = 'America/Chicago'
    allowed_domains = ['ssa42.org']
    start_urls = ['https://ssa42.org/ssa-42-meeting-dates/']
    location = {
        'name': '',
        'address': '1750 E 71st St Chicago, IL 60649',
        'neighborhood': '',
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in self._parse_items(response, upcoming=True):
            yield item

        yield scrapy.Request(
            'https://ssa42.org/minutes-of-meetings/',
            callback=self._parse_items,
        )

    def _parse_items(self, response, upcoming=False):
        """Parse items on upcoming and minutes pages"""
        today = datetime.now().date()
        for item in response.css('article.entry p'):
            text = item.xpath('./text()').extract_first()
            if not re.match(r'.*day, .*\d{4}', text):
                continue
            start = self._parse_start(text)
            if not start['date'] or (upcoming and start['date'] < today):
                continue
            data = {
                '_type': 'event',
                'name': self._parse_name(text),
                'event_description': '',
                'classification': COMMISSION,
                'start': start,
                'end': {
                    'date': start['date'],
                    'time': None,
                    'note': '',
                },
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(item),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }],
            }
            data['status'] = self._generate_status(data, text=text)
            data['id'] = self._generate_id(data)
            yield data

    def _parse_name(self, text):
        """
        Parse or generate event name.
        """
        name = 'SSA #42 Commission'
        if 'closed' in text.lower():
            return '{} - Closed Meeting'.format(name)
        return name

    def _parse_start(self, text):
        """
        Parse start date and time.
        """
        date_match = re.search(r'[a-zA-Z]{3,9} \d{1,2}([a-z,]{1,3})? \d{4}', text)
        time_match = re.search(r'\d{1,2}:\d{2}[ pam\.]{2,5}', text)
        if date_match:
            try:
                date_str = re.sub(
                    r'(?<=\d)[a-z]{2}',
                    '',
                    date_match.group().replace(',', ''),
                )
                dt = datetime.strptime(date_str, '%B %d %Y').date()
            except ValueError:
                dt = None
        if time_match:
            time_str = time_match.group().replace('.', '').replace(' ', '')
            tm = datetime.strptime(time_str, '%I:%M%p').time()
        else:
            tm = time(10)
        return {
            'date': dt,
            'time': tm,
            'note': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        docs = []
        for doc in item.css('a'):
            doc_text = doc.xpath('./text()').extract_first()
            if 'agenda' in doc_text.lower():
                doc_note = 'Agenda'
            elif 'minutes' in doc_text.lower():
                doc_note = 'Minutes'
            else:
                doc_note = doc_text
            docs.append({'url': doc.attrib['href'], 'note': doc_note})
        return docs
