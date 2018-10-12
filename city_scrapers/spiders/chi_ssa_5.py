# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

import scrapy

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiSsa5Spider(Spider):
    name = 'chi_ssa_5'
    agency_name = 'Chicago Special Service Area #5 Commercial Ave'
    timezone = 'America/Chicago'
    allowed_domains = ['scpf-inc.org']
    start_urls = ['http://scpf-inc.org/ssa5/meeting-calendar/']
    location = {
        'address': '3030 E 92nd St Chicago, IL 60617',
        'name': 'MB Financial Bank',
        'neighborhood': '',
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        if 'MB Financial Bank' not in response.text:
            raise ValueError('Meeting address has changed')

        req = scrapy.Request(
            'http://scpf-inc.org/ssa5/meeting-minutes/',
            callback=self._parse_minutes,
            dont_filter=True
        )
        req.meta['items'] = self._parse_current_year(response)
        yield req

    def _parse_current_year(self, response):
        meetings = response.css('.page-post-content h2:nth-child(2)')[0]
        items = []
        for item in meetings.xpath('child::node()'):
            if isinstance(item.root, str):
                items.append({'text': item.root})
            elif item.root.tag == 'a':
                items[-1]['agenda'] = item.root.get('href')

        event_items = []
        for item in items:
            data = {
                '_type': 'event',
                'name': self._parse_name(item['text']),
                'event_description': '',
                'classification': COMMISSION,
                'start': self._parse_start(item['text']),
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(item.get('agenda')),
                'sources': [{'url': response.url, 'note': ''}],
            }
            data['end'] = {
                'date': data['start']['date'],
                'time': None,
                'note': '',
            }
            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)
            event_items.append(data)
        return event_items

    def _parse_minutes(self, response):
        """
        Parse the minutes page, matching with existing events if found
        """
        items = response.meta.get('items', [])
        for item in response.css('.page-post-content a'):
            text = item.xpath('text()').extract_first()
            start = self._parse_start(text, minutes=True)

            documents = [{
                'url': item.attrib['href'],
                'note': 'Minutes',
            }]
            date_match = [
                idx for idx, i in enumerate(items)
                if i['start']['date'] == start['date']
            ]
            if len(date_match):
                items[date_match[0]]['documents'].extend(documents)
            else:
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
                    'documents': documents,
                    'sources': [{'url': response.url, 'note': ''}],
                }
                data['status'] = self._generate_status(data, text='')
                data['id'] = self._generate_id(data)
                items.append(data)
        for item in items:
            yield item

    def _parse_name(self, text):
        """
        Parse or generate event name.
        """
        if 'special' in text.lower():
            return 'Special Commission Meeting'
        return 'Regular Commission Meeting'

    def _parse_start(self, text, minutes=False):
        """
        Parse start date and time.
        """
        parsed_date = None
        if minutes:
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
            if date_match:
                parsed_date = datetime.strptime(
                    date_match.group(), '%m/%d/%Y'
                )
        else:
            date_match = re.search(r'\w{3,9} \d{1,2}, \d{4}', text)
            if date_match:
                parsed_date = datetime.strptime(
                    date_match.group(), '%B %d, %Y'
                )
        if parsed_date:
            return {
                'date': parsed_date.date(),
                'time': time(14, 0),
                'note': '',
            }

    def _parse_documents(self, agenda):
        """
        Parse or generate documents.
        """
        if agenda:
            return [{'url': agenda, 'note': 'Agenda'}]
        return []
