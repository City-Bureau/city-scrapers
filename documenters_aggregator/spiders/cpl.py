# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

import re
import urllib.request
import json
from datetime import datetime
from pytz import timezone


class CplSpider(scrapy.Spider):
    name = 'cpl'
    long_name = 'Chicago Public Library'
    allowed_domains = ['https://www.chipublib.org/']
    start_urls = ['https://www.chipublib.org/board-of-directors/board-meeting-schedule/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        #the following code turns the HTML glob into an array of lists of strings, one list
        #per event. The first line is *always* the date, the last line is *always* the address.
        #IF the event has 3 lines, then line 2 and 3 should be concatenated to be the location.
        #Otherwise, the event has 3 lines and the middle line is the location.
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

        #grab general information for event description
        description_str = ' '.join(all_clean_events[0] + all_clean_events[1])
        #remove first two informational lines from events array
        events_only = all_clean_events[2:]
        #gets year of events

        for item in events_only:
            yr = cleanhtml(year[0])
            start_time = self._parse_start(item, yr)
            with urllib.request.urlopen("https://data.cityofchicago.org/resource/psqp-6rmg.json") as url:
                lib_info = json.loads(url.read().decode())
            yield {
                '_type': 'event',
                'id': self._generate_id(start_time),
                'name': 'Chicago Public Library Board Meeting',
                'description': description_str,
                'classification': 'Board meeting',
                'start_time': self._parse_start(item, yr),
                'end_time': None,  # no end time listed
                'all_day': False,  # default is false
                'status': self._parse_status(item),  # default is tentative, but there is no status info on site
                'location': self._parse_location(item, lib_info),
                'sources': self._parse_sources(response)
            }

    def _generate_id(self, start_time):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        date = start_time.split('T')[0]
        dashified = re.sub(r'[^a-z]+', '-', 'cpl')
        return '{0}-{1}'.format(date, dashified)

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        @TODO determine correct status
        """
        return 'tentative'

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
                return match['address'] + ', ' + match['city'] + ' ' + match['state'] + ' ' + match['zip']
        """
            def test(item):
                for i in range(len(lib_info)):
                    print (i, lib_info.iloc[i])

        ev_zero.address + ', ' + ev_zero.city + ' ' + ev_zero.state + ' ' + str(ev_zero.zip)
        """

    def _parse_start(self, item, year):
        """
        Parse start date and time.
        """
        #s = response.css('strong::text').extract()
        #tz = timezone('America/Chicago')
        #TODO: turn every event array's first string into correct date format
        date = item[0]
        date = date.replace(',', '')
        date = date.replace('.', '')
        date = date + ' ' + year
        datetime_object = datetime.strptime(date, '%A %B %d %I %p %Y')
        tz = timezone('America/Chicago')
        return tz.localize(datetime_object).isoformat()

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
