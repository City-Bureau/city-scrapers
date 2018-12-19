# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import datetime
import json
import re

import requests

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiLibrarySpider(Spider):
    name = 'chi_library'
    agency_name = 'Chicago Public Library'
    timezone = 'America/Chicago'
    allowed_domains = ['https://www.chipublib.org/']
    start_urls = ['https://www.chipublib.org/board-of-directors/board-meeting-schedule/']

    def __init__(self, *args, session=requests.Session(), **kwargs):
        """
        Initialize a spider with a session object to use in the
        _get_lib_info function.
        """
        super().__init__(*args, **kwargs)
        self.session = session

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # the following code turns the HTML glob into an array of lists of strings, one list
        # per event. The first line is *always* the date, the last line is *always* the address.
        # If the event has 3 lines, then line 2 and 3 should be concatenated to be the location.
        # Otherwise, the event has 3 lines and the middle line is the location.
        events = response.css('div.entry-content p').extract()
        year = response.css('div.entry-content h2').extract()

        def cleanhtml(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        all_clean_events = []
        for val in events:
            clean_event = cleanhtml(val)
            final_event = clean_event.splitlines()
            all_clean_events.append(final_event)

        # grab general information for event description
        description_str = ' '.join(all_clean_events[0] + all_clean_events[1])
        # remove first two informational lines from events array
        events_only = all_clean_events[2:]
        # get library info from City of Chicago API
        lib_info = self._get_lib_info()

        for item in events_only:
            yr = cleanhtml(year[0])
            start_time = self._parse_start(item, yr)
            data = {
                '_type': 'event',
                'name': 'Board of Directors',
                'description': description_str,
                'classification': BOARD,
                'start': {
                    'date': start_time.date(),
                    'time': start_time.time(),
                    'note': '',
                },
                'end': {
                    'date': None,
                    'time': None,
                    'note': '',
                },
                'all_day': False,
                'location': self._parse_location(item, lib_info),
                'documents': self._parse_documents(start_time),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data)
            yield data

    def _get_lib_info(self):
        """
        Returns a list of dictionaries of information about each library
        from the City of Chicago's API.
        """
        r = self.session.get("https://data.cityofchicago.org/resource/psqp-6rmg.json")
        return json.loads(r.text)

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def find_name(self, li):
        if len(li) == 4:
            return ', '.join(li[1:3])
        else:
            return li[1]

    def _parse_location(self, item, lib_info):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': self.find_name(item),
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
            'address': self._parse_address(item, lib_info)
        }

    def _parse_address(self, item, lib_info):
        """
        compare item's address line to library API addresses until you find the match,
        then concatenate address line with city/state/zip to return address and maybe url?
        """
        if len(item) == 4:
            addr = 3
        else:
            addr = 2

        for i in range(len(lib_info)):
            if item[addr] == lib_info[i]['address']:
                match = lib_info[i]
                return match['address'] + ', ' + match['city'] + ' ' + match['state'] + ' ' + match[
                    'zip']

    def _parse_start(self, item, year):
        """
        Parse start date and time.
        """
        # TODO: turn every event array's first string into correct date format
        date = item[0]
        date = date.replace(',', '')
        date = date.replace('.', '')
        date = date + ' ' + year
        return datetime.datetime.strptime(date, '%A %B %d %I %p %Y')

    def _parse_documents(self, start_time):
        """Check if agenda and minutes are valid URLs, add to documents if so"""
        agenda_url = (
            'https://www.chipublib.org/news/board-of-directors-'
            'meeting-agenda-{}-{date.day}-{date.year}/'
        ).format(
            start_time.strftime('%B').lower(),
            date=start_time,
        )
        minutes_url = agenda_url.replace('agenda', 'minutes')
        agenda_res = self.session.get(agenda_url)
        minutes_res = self.session.get(minutes_url)
        documents = []
        if agenda_res.status_code == 200:
            documents.append({
                'url': agenda_url,
                'note': 'Agenda',
            })
        if minutes_res.status_code == 200:
            documents.append({
                'url': minutes_url,
                'note': 'Minutes',
            })
        return documents

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
