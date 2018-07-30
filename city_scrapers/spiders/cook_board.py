# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime, timedelta
from pytz import timezone
from legistar.events import LegistarEventsScraper

from city_scrapers.spider import Spider


class Cook_boardSpider(Spider):
    name = 'cook_board'
    agency_id = 'Cook County Board of Commissioners'
    timezone = 'America/Chicago'
    allowed_domains = ['cook-county.legistar.com']
    start_urls = ['https://www.cook-county.legistar.com']

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
        les = LegistarEventsScraper(requests_per_minute=0)
        les.EVENTSPAGE = 'https://cook-county.legistar.com/Calendar.aspx'
        les.BASE_URL = 'https://cook-county.legistar.com'
        if not since:
            since = datetime.today().year
        return les.events(since=since)

    def _parse_events(self, events):
        for item, _ in events:
            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'event_description': self._parse_description(item),
                'classification': self._parse_classification(name),
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
                'documents': self._parse_documents(item)
            }
            data['status'] = self._generate_status(data, item['Meeting Location'])
            data['id'] = self._generate_id(data)
            yield data

    def _parse_documents(self, item):
        """
        Returns meeting details and agenda if available.
        """
        documents = []
        details = item['Meeting Details']
        if type(details) == dict:
            documents.append({
                'note': 'Meeting Details',
                'url': details['url']
            })
        agenda = item['Agenda']
        if type(agenda) == dict:
            documents.append({
                'note': 'Agenda',
                'url': agenda['url']
            })
        return documents

    def _parse_classification(self, name):
        """
        Differentiate board and committee meetings
        based on event name.
        """
        if 'board' in name.lower():
            return 'Board'
        else:
            return 'Committee'

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        address = item['Meeting Location'].split('/n')[0]
        return {
            'address': address,
            'name': '',
            'neighborhood': ''
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item['Name']['label']

    def _parse_description(self, item):
        """
        No description listed.
        """
        return ''

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
            return {
                'date': start_datetime.date(),
                'time': start_datetime.time(),
                'note': ''
            }
        return {
            'date': None,
            'time': None,
            'note': ''
        }

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
        return {
            'date': None,
            'time': None,
            'note': ''
        }

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except:
            url = 'https://cook-county.legistar.com/Calendar.aspx'
        return [{'url': url, 'note': ''}]
