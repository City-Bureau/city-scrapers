# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import os
import json
from datetime import datetime
from pytz import timezone
from enum import IntEnum

import scrapy
from dateutil.rrule import rrule, MONTHLY, WEEKLY, MO, TU, WE, TH, FR, SA, SU

GOOGLE_API_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_GOOGLE_API_KEY') or 'test-token'
SPREADSHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/1xnt4kZI9Ruinw91wM-nnWftsFD-ZaKaozepdNXeIrpo'


class Calendar(object):
    """
    This object is a wrapper around the `python-dateutil` module, providing a
    much simpler interface that can handle our limited set of use cases.
    """

    DAYS = {'monday': MO, 'tuesday': TU, 'wednesday': WE, 'thursday': TH, 'friday': FR, 'saturday': SA, 'sunday': SU}

    def __init__(self, start_date=datetime.today()):
        self.start_date = start_date

    def nth_weekday(self, n, day_of_week, count=3):
        """
        Return a list of datetime.date objects representing the next instances of
        the specified weekday in a month. This is used, for example, to get a list of
        the upcoming "third Thursdays of the month":

        `cal.nth_weekday(3, 'thursday')`

        `n` should be which day to return.
        `day_of_week` should be one of the keys in DAYS.
        `count` is option and is the number of dates to return.
        """

        assert isinstance(n, int), 'n must be an int'
        self._assert_day_of_week(day_of_week)

        day = self.DAYS[day_of_week](n)
        datetimes = list(rrule(MONTHLY, count=count, byweekday=day, dtstart=self.start_date))
        return [datetime.date(d) for d in datetimes]

    def last_weekday(self, day_of_week, count=3):
        """
        Return a list of datetime.date objects representing the next instances of
        the last specified weekday in a month. This is used, for example, to get a list of
        the upcoming "last Fridays of the month":

        `cal.last_weekday('friday')`

        `day_of_week` should be one of the keys in DAYS.
        `count` is option and is the number of dates to return.
        """
        return self.nth_weekday(-1, day_of_week, count)

    def weekday(self, day_of_week, count=3):
        """
        Return a list of datetime.date objects representing the next instances of
        the specified weekday. This is used, for example, to get a list of
        the upcoming Tuesdays:

        `cal.weekday('tuesday')`

        `day_of_week` should be one of the keys in DAYS.
        `count` is option and is the number of dates to return.
        """
        self._assert_day_of_week(day_of_week)

        day = self.DAYS[day_of_week]
        datetimes = list(rrule(WEEKLY, count=count, byweekday=day, dtstart=self.start_date))
        return [datetime.date(d) for d in datetimes]

    def _assert_day_of_week(self, day_of_week):
        assert day_of_week in self.DAYS, 'n must be one of {0}'.format(' '.join(self.DAYS.values))


class Row(IntEnum):
    """
    This enum makes working with the data rows more pleasant.
    """

    ALDERMAN = 0            # Text
    PHONE = 1               # Text
    WEBSITE = 2             # Text
    WARD = 3                # Text
    DOCUMENTER = 4          # Text
    ADDRESS = 5             # Text
    HAS_WARD_NIGHTS = 6     # Yes, No
    FREQUENCY = 7           # Weekly, Monthly (1st occurrence), Monthly (2nd occurrence),
    #                       # Monthly (3rd occurrence), Monthly (4th occurrence),
    #                       # Monthly (last occurrence), Irregularly
    DAY_OF_WEEK = 8         # Monday, Tuesday, Wednesday, Thursday, Friday,
    #                       # Saturday, Sunday
    START_TIME = 9          # [h]h:mm am
    END_TIME = 10           # [h]h:mm am
    SIGN_UP_REQUIRED = 11   # Yes, No
    SIGN_UP_INFO = 12       # Text
    INFO = 13               # Text


class WardNightSpider(scrapy.Spider):
    name = 'ward_night'
    allowed_domains = ['sheets.googleapis.com/v4/']
    start_urls = []  # assigned in __init__

    def __init__(self, google_api_key=GOOGLE_API_KEY, spreadsheet_url=SPREADSHEET_URL, *args, **kwargs):
        super(WardNightSpider, self).__init__(*args, **kwargs)
        self.start_urls = [spreadsheet_url + '/values/A3:N100?key=' + google_api_key]

    def parse(self, response):
        """
        Yields a dictionary with the required keys.
        """

        rows = json.loads(response.body.decode('utf-8'))['values']

        for row in rows:
            # The JSON omits values for trailing columns with no values. By padding
            # the rows out, the rest of the code can assume there will always be 10 columns.
            missing_values = 14 - len(row)
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

        return row[Row.INFO]

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
