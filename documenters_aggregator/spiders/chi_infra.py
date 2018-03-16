# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import datetime as dt

from documenters_aggregator.spider import Spider


class Chi_infraSpider(Spider):
    name = 'chi_infra'
    long_name = 'Chicago Infrastructure Trust'
    allowed_domains = ['chicagoinfrastructure.org']
    start_urls = ['http://chicagoinfrastructure.org/public-records/scheduled-meetings/']

    year = str(dt.datetime.now().year)

    def parse(self, response):
        """
        Currently, the meeting page just gives dates, so there's limited info to report.
        The dates have no years, but the list has a year at the top. I pull this
        to add to the datetimes.
        """
        entries = response.css('div.entry')[0].css('div.entry p').extract()
        self._parse_year(entries)
        for item in entries:
            start_time = self._parse_start(item)
            if not start_time:
                continue
            data = {
                '_type': 'event',
                'name': 'Board Meeting',
                'description': None,
                'classification': 'Board Meeting',
                'start_time': start_time,
                'end_time': None,
                'all_day': False,
                'timezone': 'America/Chicago',
                'status': 'tentative',
                'location': self._parse_location(item),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data, start_time)
            yield data

    def _parse_year(self, entries):
        """
        Look for a string of 4 numbers to be the year.
        If not found, use current year.
        """
        for entry in entries:
            year_match = re.search(r'([0-9]{4})', entry)
            if year_match:
                self.year = year_match.group(1)
                break

    def _parse_start(self, item):
        """
        No times given; set to Midnight
        """
        match = re.search(r'([a-zA-Z]*),\s{1}([a-zA-Z]+)\s([0-9]{1,2})', item)
        try:
            date_string = '{0} {1}'.format(match.group(0), self.year)
        except:
            return None
        else:
            start_date = dt.datetime.strptime(date_string, "%A, %B %d %Y")
            return self._naive_datetime_to_tz(start_date, 'America/Chicago')

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]

    def _parse_location(self, item):
        """
        No location provided
        """
        return {
            'url': None,
            'name': None,
            'address': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            }
        }
