# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime
from pytz import timezone
from legistar.events import LegistarEventsScraper

from documenters_aggregator.spider import Spider


class Cook_boardSpider(Spider):
    name = 'cook_board'
    long_name = 'Cook County Board of Commissioners'
    allowed_domains = ['cook-county.legistar.com']
    start_urls = ['https://www.cook-county.legistar.com']  # use LegistarEventsScraper instead

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
        les = LegistarEventsScraper(jurisdiction=None, datadir=None)
        les.EVENTSPAGE = 'https://cook-county.legistar.com/Calendar.aspx'
        les.BASE_URL = 'https://cook-county.legistar.com'
        if not since:
            since = datetime.today().year
        return les.events(since=since)

    def _parse_events(self, events):
        for item, _ in events:
            start_time = self._parse_start(item)
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': start_time.isoformat(),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'timezone': 'America/Chicago',
                'location': self._parse_location(item),
                'sources': self._parse_sources(item)
            }
            data['status'] = self._parse_status(item, data['start_time'])
            data['id'] = self._generate_id(data, start_time)
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
        if datetime.now().isoformat() > start_time:
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
            'name': item.get('Meeting Location', None),
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
        return item['Name']['label']

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        agenda = item['Agenda']
        return ("The Cook County Board of Commissioners is the governing board and"
                "legislative body of the county. It is comprised of 17 Commissioners,"
                "each serving a four-year term and is elected from single member districts."
                "Each district represents approximately 300,000 residents. County Commissioners"
                "are elected officials who oversee county" 
                "activities and work to ensure that citizen concerns are met," 
                "federal and state requirements are fulfilled, and county operations run smoothly.")

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        time = item.get('Meeting Time', None)
        date = item.get('Meeting Date', None)
        if date and time:
            time_string = '{0} {1}'.format(date, time)
            naive = datetime.strptime(time_string, '%m/%d/%Y %I:%M %p')
            tz = timezone('America/Chicago')
            return tz.localize(naive)
        return None

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return None

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except:
            url = 'https://cook-county.legistar.com/Calendar.aspx'
        return [{'url': url, 'note': ''}]
