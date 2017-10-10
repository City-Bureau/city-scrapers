# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

from datetime import datetime, timedelta
from pytz import timezone
import time as Time

class WardNightSpider(scrapy.Spider):
    name = 'ward_night'
    #allowed_domains = ['']
    #start_urls = ['']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

    def parse_event_page(self, response):
        return {
            '_type': 'event',
            'id': self._parse_id(response),
            'name': self._parse_name(response),
            'description': self._parse_description(response),
            'classification': self._parse_classification(response),
            'start_time': self._parse_date_time(response)['start'],
            'end_time': self._parse_date_time(response)['end'],
            'all_day': self._parse_all_day(response),
            'status': self._parse_status(response),
            'location': self._parse_location(response),
        }

    def _parse_id(self, response):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """

    def _parse_classification(self, response):
        """
        Parse or generate classification (e.g. town hall).
        """

    def _parse_status(self, response):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': '',
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date_time_extract = self._extract_date_time(response)
        if 'all day' in date_time_extract:
            return True
        return False

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        

    def _parse_description(self, response):
        """
        Parse or generate event name.
        """

    def _extract_date_time(self, response):
        '''
        Extract string with date, start time, end time
        '''

    def _parse_date_time(self, response):
        """
        Parse start-date-time and end-date-time
        """

    def _make_date(self, date, time):
        """
        Combine year, month, day with variable time and export as timezone-aware,
        ISO-formatted string.
        """
        time_string = '{0} {1}'.format(date, time)

        try:
            naive = datetime.strptime(time_string, '%b %d %Y %I:%M%p')
        except ValueError:
            return None

        tz = timezone('America/Chicago')
        return tz.localize(naive).isoformat()