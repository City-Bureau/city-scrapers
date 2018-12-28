# -*- coding: utf-8 -*-
from datetime import datetime

from legistar.events import LegistarEventsScraper

from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class DetGreatLakesWaterAuthoritySpider(Spider):
    name = 'det_great_lakes_water_authority'
    agency_name = 'Detroit Great Lakes Water Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['glwater.legistar.com']
    start_urls = ['https://glwater.legistar.com/']

    def _make_legistar_call(self, since=None):
        les = LegistarEventsScraper()
        les.EVENTSPAGE = 'https://glwater.legistar.com/Calendar.aspx'
        les.BASE_URL = 'https://glwater.legistar.com'
        if not since:
            since = datetime.today().year
        return les.events(since=since)

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.gitbooks.io/documenters-event-aggregator/event-schema.html>.
        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        events = self._make_legistar_call()
        return self._parse_events(events)

    def _parse_events(self, events):
        for item, _ in events:
            start = self._parse_start(item)
            data = {
                '_type': 'event',
                'name': item['Name'],
                'event_description': '',
                'classification': self._parse_classification(item['Name']),
                'start': start,
                'end': {
                    'date': start['date'],
                    'time': None,
                    'note': ''
                },
                'all_day': False,
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
                'documents': self._parse_documents(item)
            }

            data['status'] = self._generate_status(data, item['Meeting Time'])
            data['id'] = self._generate_id(data)
            yield data

    def _parse_documents(self, item):
        """
        Parse meeting minutes and agenda if available.
        """
        documents = []
        for doc in ['Agenda', 'Minutes', 'Video', 'ePacket']:
            if isinstance(item.get(doc), dict) and item[doc].get('url'):
                documents.append({'url': item[doc]['url'], 'note': item[doc].get('label', doc)})
        return documents

    def _parse_classification(self, name):
        if 'board' in name.lower():
            return BOARD
        elif 'committee' in name.lower():
            return COMMITTEE
        return NOT_CLASSIFIED

    def _parse_location(self, item):
        """
        Parse location
        """
        addr_str = item.get('Meeting Location', '')
        if 'water board building' in addr_str.lower():
            return {
                'name': 'Water Board Building',
                'address': '735 Randolph St Detroit, MI 48226',
                'neighborhood': '',
            }
        return {
            'name': '',
            'address': addr_str,
            'neighborhood': '',
        }

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        time_str = item.get('Meeting Time', None)
        date_str = item.get('Meeting Date', None)
        if time_str == 'Canceled' or not time_str:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
            return {'date': dt.date(), 'time': None, 'note': ''}
        else:
            dt_str = '{} {}'.format(date_str, time_str)
            dt = datetime.strptime(dt_str, '%m/%d/%Y %I:%M %p')
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except Exception:
            url = 'https://glwater.legistar.com/Calendar.aspx'
        return [{'url': url, 'note': ''}]
