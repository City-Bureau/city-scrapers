# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import urllib3

from datetime import datetime
from legistar.events import LegistarEventsScraper

from documenters_aggregator.spider import Spider


class Chi_parksSpider(Spider):
    name = 'chi_parks'
    long_name = 'Chicago Park District'
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
        les = LegistarEventsScraper(jurisdiction=None, datadir=None)
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
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'timezone': 'America/Chicago',
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
            }
            data['id'] = self._generate_id(data, data['start_time'])
            data['status'] = self._parse_status(item, data['start_time'])
            yield data

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, item, start_time):
        """
        passed = meeting already started
        tentative = no agenda posted
        confirmed = agenda posted
        """
        if datetime.now().isoformat() > start_time.isoformat():
            return 'passed'
        if 'url' in item['Agenda']:
            return 'confirmed'
        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'address': self.clean_html(item.get('Meeting Location', None)),
            'name': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
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
        return item['Name']

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return ("The Chicago Park District Act provides that the Chicago"
                "Park District shall be governed by a board of seven" 
                "non-salaried Commissioners who are appointed by the Mayor"
                "of the City of Chicago with the approval of the Chicago City"
                "Council. Under the Chicago Park District Code, the Commissioners"
                "have a fiduciary duty to act, vote on all matters, and govern"
                "the Park District in the best interest of the Park District.")

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        time = item.get('Meeting Time', None)
        date = item.get('Meeting Date', None)
        if date and time:
            time_string = '{0} {1}'.format(date, time)
            naive = datetime.strptime(time_string, '%m/%d/%Y %I:%M %p')
            return self._naive_datetime_to_tz(naive)
        return None

    def _parse_end(self, item):
        """
        No end date.
        """
        return None

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
