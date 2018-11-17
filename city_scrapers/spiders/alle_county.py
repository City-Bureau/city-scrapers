# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime, timedelta

import urllib3
from legistar.events import LegistarEventsScraper

from city_scrapers.constants import CITY_COUNCIL, COMMITTEE, FORUM
from city_scrapers.spider import Spider


class AlleCountySpider(Spider):
    name = 'alle_county'
    agency_name = 'Allegheny County Government'
    timezone = 'America/New_York'
    allowed_domains = ['alleghenycounty.legistar.com']
    START_URL = 'https://alleghenycounty.legistar.com'
    start_urls = [START_URL]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows
        the `Open Civic Data event standard
        <http://docs.opencivicdata.org/en/latest/data/event.html>`.

        Change the `_parse_id`, `_parse_name`, etc methods
        to fit your scraping needs.
        """
        events = self._make_legistar_call()
        return self._parse_events(events)

    def _make_legistar_call(self, since=None):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        les = LegistarEventsScraper()
        les.EVENTSPAGE = self.START_URL + '/Calendar.aspx'
        les.BASE_URL = self.START_URL
        if not since:
            since = datetime.today().year
        return les.events(since=since)

    def _parse_events(self, events):
        for item, _ in events:
            data = {
                'timezone': self.timezone,
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
            data['status'] = self._generate_status(data, item['Meeting Location'])
            yield data

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        Room = item.get('Meeting Location', None)
        if Room:
            Room = Room + ','

        return {
            'address':
                "{Room} {Location}".format(
                    Room=Room, Location=('436 Grant Street, '
                                         'Pittsburgh, PA 15219')
                ),
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

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings.
        """
        meeting_loc_str = item['Meeting Location'].lower()
        if 'hearing' in meeting_loc_str:
            return FORUM
        if 'committee' in meeting_loc_str:
            return COMMITTEE
        return CITY_COUNCIL

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        documents = []
        details = item['Minutes']
        if isinstance(details, dict):
            documents.append({'note': 'Minutes', 'url': details['url']})
        agenda = item['Agenda']
        if isinstance(agenda, dict):
            documents.append({'note': 'Agenda', 'url': agenda['url']})
        return documents

    def _parse_start_datetime(self, item):
        """
        Parse the start datetime.
        """
        time = item.get('Meeting Time', None)
        date = item.get('Meeting Date', None)
        time_string = '{0} {1}'.format(date, time)
        return (datetime.strptime(time_string, '%m/%d/%Y %I:%M %p'))

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        datetime_obj = self._parse_start_datetime(item)
        return {'date': datetime_obj.date(), 'time': datetime_obj.time(), 'note': ''}

    def _parse_end(self, item):
        """
        No end date listed. Estimate 3 hours after start time.
        """
        datetime_obj = self._parse_start_datetime(item)
        return {
            'date': datetime_obj.date(),
            'time': ((datetime_obj + timedelta(hours=3)).time()),
            'note': 'Estimated 3 hours after start time'
        }

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except ValueError:
            url = self.START_URL + r'/Calendar.aspx'
        return [{'url': url, 'note': ''}]
