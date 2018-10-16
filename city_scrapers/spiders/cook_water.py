# -*- coding: utf-8 -*-

from datetime import datetime
from legistar.events import LegistarEventsScraper

from city_scrapers.constants import BOARD, COMMITTEE, FORUM
from city_scrapers.spider import Spider


class CookWaterSpider(Spider):
    name = 'cook_water'
    agency_name = 'Metropolitan Water Reclamation District of Greater Chicago'
    allowed_domains = ['mwrd.legistar.com']
    event_timezone = 'America/Chicago'
    start_urls = ['https://mwrd.legistar.com']
    # TODO confirming this is correct address Issue #386
    address = '100 East Erie Street Chicago, IL 60611'
    neighborhood = 'River North'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.gitbooks.io/documenters-event-aggregator/event-schema.html>.
        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        # if legistar, different parse method or template required
        # (needs documentation)
        events = self._make_legistar_call()
        return self._parse_events(events)

    def _make_legistar_call(self, since=None):
        les = LegistarEventsScraper(requests_per_minute=0)
        les.EVENTSPAGE = 'https://mwrd.legistar.com/Calendar.aspx'
        les.BASE_URL = 'https://mwrd.legistar.com'
        if not since:
            since = datetime.today().year
        return les.events(since=since)

    def _parse_events(self, events):
        for item in events:
            item = item[0]
            name = self._parse_name(item)
            if name == 'Study Session':
                continue

            start = self._parse_start(item)
            data = {
                '_type': 'event',
                'name': name,
                'event_description': '',
                'classification': self._parse_classification(name),
                'start': start,
                'end': {
                    'date': start['date'],
                    'time': None,
                    'note': '',
                },
                'all_day': False,
                'timezone': self.event_timezone,
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
                'documents': self._parse_documents(item)
            }
            data['status'] = self._generate_status(
                data, item['Meeting Location']
            )
            data['id'] = self._generate_id(data)
            yield data

    def _parse_documents(self, item):
        """
        Parse meeting details and agenda if available.
        """
        documents = []
        details = item['Meeting Details']
        if type(details) == dict:
            documents.append({
                'url': details['url'], 'note': 'Meeting details'
            })
        agenda = item['Agenda']
        if type(agenda) == dict:
            documents.append({
                'url': agenda['url'], 'note': 'Agenda'
            })
        return documents

    def _parse_classification(self, name):
        """
        Parse or generate classification (e.g. town hall).
        """
        if 'committee' in name.lower():
            return COMMITTEE
        if 'hearing' in name.lower():
            return FORUM
        return BOARD

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'name': item.get('Meeting Location', None),
            'address': self.address,
            'neighborhood': self.neighborhood
        }

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item['Name']['label']

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        time = item.get('Meeting Time', None)
        date = item.get('Meeting Date', None)
        # some meetings have no time entered, this was effecting scraper
        # results this could use better error handilng
        if date and time:
            time_string = '{0} {1}'.format(date, time)
            naive = datetime.strptime(time_string, '%m/%d/%Y %I:%M %p')
            return {'date': naive.date(),
                    'time': naive.time(),
                    'note': ''}
        elif not time:
            time_string = '{0}'.format(date)
            naive = datetime.strptime(time_string, '%m/%d/%Y')
            return {'date': naive.date(),
                    'time': None,
                    'note': ''}

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        try:
            url = item['Name']['url']
        except:
            url = 'https://mwrd.legistar.com/Calendar.aspx'
        return [{'url': url, 'note': ''}]
