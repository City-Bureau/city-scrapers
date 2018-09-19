# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import urllib3

from datetime import datetime, date, time, timedelta
from legistar.events import LegistarEventsScraper

from city_scrapers.constants import BOARD, FORUM
from city_scrapers.spider import Spider


class ChiParksSpider(Spider):
    name = 'chi_parks'
    agency_name = 'Chicago Park District'
    START_URL = 'https://chicagoparkdistrict.legistar.com'
    allowed_domains = ['chicagoparkdistrict.legistar.com']
    start_urls = [START_URL]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        events = self._make_legistar_call()
        return self._parse_events(events)

    def _make_legistar_call(self, since=None):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        les = LegistarEventsScraper(requests_per_minute=0)
        les.EVENTSPAGE = self.START_URL + '/Calendar.aspx'
        les.BASE_URL = self.START_URL
        if not since:
            since = datetime.today().year
        return les.events(since=since)

    def _parse_events(self, events):
        for item, _ in events:
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': '',
                'all_day': self._parse_all_day(item),
                'classification': self._parse_classification(item),
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'location': self._parse_location(item),
                'documents': self._parse_documents(item),
                'sources': self._parse_sources(item),
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')
            yield data

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        return {
            'address': self.clean_html(item.get('Meeting Location', None)),
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
        board_str = 'Board of Commissioners'
        if item['Name'].strip() == board_str:
            return board_str
        return '{}: {}'.format(board_str, item['Name'])

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings.
        """
        if 'hearing' in item['Name'].lower():
            return FORUM
        return BOARD

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        documents = []

        # Add meetings details if available
        info = item['Meeting Details']
        try:
            url = info['url']
        except (TypeError, KeyError):
            pass
        else:
            documents.append({'url': url, 'note': 'Meeting Details'})

        # Add agenda if available
        info = item['Agenda']
        try:
            url = info['url']
        except (TypeError, KeyError):
            pass
        else:
            documents.append({'url': url, 'note': 'Agenda'})
        return documents

    def _parse_start_datetime(self, item):
        """
        Parse the start datetime.
        """
        time = item.get('Meeting Time', None)
        date = item.get('Meeting Date', None)
        time_string = '{0} {1}'.format(date, time)
        return datetime.strptime(time_string, '%m/%d/%Y %I:%M %p')

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        datetime_obj = self._parse_start_datetime(item)
        return {
            'date': datetime_obj.date(),
            'time': datetime_obj.time(),
            'note': ''
        }

    def _parse_end(self, item):
        """
        No end date listed. Estimate 3 hours after start time.
        """
        datetime_obj = self._parse_start_datetime(item)
        return {
            'date': datetime_obj.date(),
            'time': (datetime_obj + timedelta(hours=3)).time(),
            'note': 'Estimated 3 hours after start time'
        }

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except:
            url = self.START_URL + '/Calendar.aspx'
        return [{'url': url, 'note': ''}]

    # TODO move to parent class?
    @staticmethod
    def clean_html(html):
        """
        Clean up HTML artifacts.
        """
        if html is None:
            return None
        else:
            clean = re.sub(r'\s*(\r|\n|(--em--))+\s*', ' ', html)
            return clean.strip()
