# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
from datetime import datetime, timedelta

from legistar.events import LegistarEventsScraper

from city_scrapers.constants import CITY_COUNCIL
from city_scrapers.spider import Spider


class ChiCityCouncilSpider(Spider):
    name = 'chi_citycouncil'
    agency_name = 'Chicago City Council'
    timezone = 'America/Chicago'
    allowed_domains = ['chicago.legistar.com']
    start_urls = ['https://chicago.legistar.com/Calendar.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        events = self._make_legistar_call()
        return self._parse_events(events)

    def _make_legistar_call(self, since=None):
        les = LegistarEventsScraper()
        les.EVENTSPAGE = 'https://chicago.legistar.com/Calendar.aspx'
        les.BASE_URL = 'https://chicago.legistar.com'
        if not since:
            since = self.year
        return les.events(since=self.year)

    def _parse_events(self, events):
        for item, _ in events:
            data = {
                '_type': 'event',
                'name': item['Name']['label'],
                'event_description': '',
                'classification': CITY_COUNCIL,
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': False,
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
                'documents': self._parse_documents(item)
            }
            data['status'] = self._generate_status(data, item['Meeting Location'])
            data['id'] = self._generate_id(data)
            yield data

    def _parse_documents(self, item):
        """
        Returns meeting minutes and agenda if available.
        """
        documents = []
        for doc in ['Agenda', 'Minutes', 'Summary', 'Video', 'Captions']:
            if isinstance(item.get(doc), dict) and item[doc].get('url'):
                documents.append({'url': item[doc]['url'], 'note': doc})
        return documents

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        split_location = item['Meeting Location'].split(' -- ')
        loc_name = 'City Hall'
        if len(split_location) > 0:
            loc_name = '{}, City Hall'.format(split_location[0])
        return {
            'address': '121 N LaSalle St Chicago, IL 60602',
            'name': loc_name,
            'neighborhood': '',
        }

    def _parse_start_datetime(self, item):
        """
        Return the start date and time as a datetime object.
        """
        time = item.get('Meeting Time', None)
        date = item.get('Meeting Date', None)
        if date and time:
            time_string = '{0} {1}'.format(date, time)
            return datetime.strptime(time_string, '%m/%d/%Y %I:%M %p')
        return None

    def _parse_start(self, item):
        """
        Parse the start date and time.
        """
        start_datetime = self._parse_start_datetime(item)
        if start_datetime:
            return {'date': start_datetime.date(), 'time': start_datetime.time(), 'note': ''}
        return {'date': None, 'time': None, 'note': ''}

    def _parse_end(self, item):
        """
        No end times are listed, so estimate the end time to
        be 3 hours after the start time.
        """
        start_datetime = self._parse_start_datetime(item)
        if start_datetime:
            return {
                'date': start_datetime.date(),
                'time': (start_datetime + timedelta(hours=3)).time(),
                'note': 'Estimated 3 hours after start time'
            }
        return {'date': None, 'time': None, 'note': ''}

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except Exception:
            url = 'https://chicago.legistar.com/Calendar.aspx'
        return [{'url': url, 'note': ''}]
