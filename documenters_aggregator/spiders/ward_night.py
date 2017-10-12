# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import scrapy
import os
import json
from datetime import datetime
from pytz import timezone
from enum import IntEnum

GOOGLE_API_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_GOOGLE_API_KEY') or 'test-token'
SPREADSHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/1xnt4kZI9Ruinw91wM-nnWftsFD-ZaKaozepdNXeIrpo'


class Row(IntEnum):
    """
    This enum makes working with the data rows more pleasant.
    """

    ALDERMAN = 0
    PHONE = 1
    WEBSITE = 2
    WARD = 3
    DOCUMENTER = 4
    ADDRESS = 5
    DAY_OF_WEEK = 6
    TIME = 7
    FREQUENCY = 8
    NOTES = 9


class WardNightSpider(scrapy.Spider):
    name = 'ward_night'
    allowed_domains = ['sheets.googleapis.com/v4/']
    start_urls = []  # assigned in __init__

    def __init__(self, google_api_key=GOOGLE_API_KEY, spreadsheet_url=SPREADSHEET_URL, *args, **kwargs):
        super(WardNightSpider, self).__init__(*args, **kwargs)
        self.start_urls = [spreadsheet_url + '/values/A1:AJ100?key=' + google_api_key]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.
        """

        rows = json.loads(response.body.decode('utf-8'))['values']

        # TODO: update the URL used above to skip the first 2 rows and then delete the next two lines
        rows.pop(0)  # headers
        rows.pop(0)  # example row

        for row in rows:
            # The JSON omits values for trailing columns with no values. By padding
            # the rows out, the rest of the code can assume there will always be 10 columns.
            missing_values = 10 - len(row)
            row.extend([''] * missing_values)
            yield self._parse_row(row)

    def _parse_row(self, row):
        return {
            '_type': 'event',
            'id': self._parse_id(row),
            'name': self._parse_name(row),
            'description': self._parse_description(row),
            'classification': self._parse_classification(row),
            # 'start_time': self._parse_date_time(row)['start'],
            # 'end_time': self._parse_date_time(row)['end'],
            'all_day': self._parse_all_day(row),
            'status': self._parse_status(row),
            # 'location': self._parse_location(row),
        }

    def _parse_id(self, row):
        """
        Generate ID. We are assuming that there will only be a single event in a each ward in a single day.
        """

        values = {
            'ward': row[Row.WARD],
            'date': '2017-01-01'
        }
        id = 'ward{ward}-{date}'.format(**values)
        return id

    def _parse_name(self, row):
        """
        Create event name
        """

        values = {
            'ward': row[Row.WARD],
            'alderman': row[Row.ALDERMAN],
        }
        name = 'Ward Night with Alderman {alderman} (Ward {ward})'.format(**values)
        return name

    def _parse_classification(self, row):
        """
        Parse or generate classification (e.g. town hall).
        """

        return None

    def _parse_status(self, row):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, row):
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

    def _parse_all_day(self, row):
        """
        Parse or generate all-day status. Defaults to false.
        """

        return False

    def _parse_description(self, row):
        """
        Parse or generate event name.
        """

        return row[Row.NOTES]

    def _extract_date_time(self, row):
        '''
        Extract string with date, start time, end time
        '''

    def _parse_date_time(self, row):
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
