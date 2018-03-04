# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import os
import json
from datetime import datetime
from enum import IntEnum

from dateutil.rrule import rrule, MONTHLY, WEEKLY, MO, TU, WE, TH, FR, SA, SU

from documenters_aggregator.spider import Spider

GOOGLE_API_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_GOOGLE_API_KEY') or 'test-token'
SPREADSHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/1xnt4kZI9Ruinw91wM-nnWftsFD-ZaKaozepdNXeIrpo'


class Calendar(object):
    """
    This object is a wrapper around the `python-dateutil` module, providing a
    much simpler interface that can handle our limited set of use cases.
    """

    DAYS = {'Monday': MO, 'Tuesday': TU, 'Wednesday': WE, 'Thursday': TH,
            'Friday': FR, 'Saturday': SA, 'Sunday': SU}

    def __init__(self, start_date=datetime.today()):
        self.start_date = start_date

    def nth_weekday(self, n, day_of_week, count=3):
        """
        Return a list of datetime.date objects representing the next instances of
        the specified weekday in a month. This is used, for example, to get a list
        of the upcoming "third Thursdays of the month":

        `cal.nth_weekday(3, 'Thursday')`

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
        the last specified weekday in a month. This is used, for example, to get a
        list of the upcoming "last Fridays of the month":

        `cal.last_weekday('Friday')`

        `day_of_week` should be one of the keys in DAYS.
        `count` is option and is the number of dates to return.
        """
        return self.nth_weekday(-1, day_of_week, count)

    def weekday(self, day_of_week, count=3):
        """
        Return a list of datetime.date objects representing the next instances of
        the specified weekday. This is used, for example, to get a list of
        the upcoming Tuesdays:

        `cal.weekday('Tuesday')`

        `day_of_week` should be one of the keys in DAYS.
        `count` is option and is the number of dates to return.
        """
        self._assert_day_of_week(day_of_week)

        day = self.DAYS[day_of_week]
        datetimes = list(rrule(WEEKLY, count=count, byweekday=day,
                         dtstart=self.start_date))
        return [datetime.date(d) for d in datetimes]

    def _assert_day_of_week(self, day_of_week):
        assert day_of_week in self.DAYS, '{0} must be one of {1}'.format(day_of_week, ', '.join(self.DAYS.keys()))


class Row(IntEnum):
    """
    This enum makes working with the data rows more pleasant.
    """

    ALDERMAN = 0            # Text
    PHONE = 1               # Text
    WEBSITE = 2             # Text
    WARD = 3                # Text
    DOCUMENTER = 4          # Text
    HAS_WARD_NIGHTS = 5     # Yes, No, Unknown
    ADDRESS = 6             # Text
    FREQUENCY = 7           # Weekly, Monthly (1st occurrence), Monthly (2nd occurrence),
    #                         Monthly (3rd occurrence), Monthly (4th occurrence),
    #                         Monthly (last occurrence), Irregularly
    DAY_OF_WEEK = 8         # Monday, Tuesday, Wednesday, Thursday, Friday,
    #                         Saturday, Sunday
    START_TIME = 9          # [h]h:mm am
    END_TIME = 10           # [h]h:mm am
    SIGN_UP_REQUIRED = 11   # Yes, No
    SIGN_UP_INFO = 12       # Text
    INFO = 13               # Text


class WardNightSpider(Spider):
    name = 'ward_night'
    long_name = 'Ward Nights'
    allowed_domains = ['sheets.googleapis.com/v4/']
    start_urls = [SPREADSHEET_URL + '/values/A3:N100?key=' + GOOGLE_API_KEY]

    def __init__(self, start_date=datetime.today(), *args, **kwargs):
        super(WardNightSpider, self).__init__(*args, **kwargs)
        self.start_date = start_date

    def parse(self, response):
        """
        Yields a dictionary with the required keys.
        """

        rows = json.loads(response.body.decode('utf-8'))['values']

        for row in rows:
            # Strip leading or trailing whitespace from all values
            for i in range(len(row)):
                row[i] = row[i].strip()

            # The JSON omits values for trailing columns with no values. By padding
            # the rows out, the rest of the code can assume there will always be 14
            # columns.
            missing_values = 14 - len(row)
            row.extend([''] * missing_values)
            for result in self._parse_row(row):
                yield result

    def _days_for_frequency(self, frequency, day_of_week):
        calendar = Calendar(self.start_date)
        occurance_map = ['Monthly (1st occurrence)', 'Monthly (2nd occurrence)',
                         'Monthly (3rd occurrence)', 'Monthly (4th occurrence)']

        if frequency in occurance_map:
            n = occurance_map.index(frequency) + 1
            return calendar.nth_weekday(n, day_of_week)
        elif frequency == 'Weekly':
            return calendar.weekday(day_of_week)
        elif frequency == 'Monthly (last occurrence)':
            return calendar.last_weekday(day_of_week)
        else:
            # also handles 'Irregularly'
            return []

    def _parse_row(self, row):

        if row[Row.HAS_WARD_NIGHTS] != 'Yes':
            return []

        try:
            assert len(row[Row.START_TIME]) > 0, 'start time must have a value'
            assert len(row[Row.END_TIME]) > 0, 'end time must have a value'
        except:
            self.logger.error('event has invalid start or end time:')
            self.logger.error(row)
            return []

        def build_event(day):
            dates = self._parse_date_time(row, day)
            data = {
                '_type': 'event',
                'name': self._parse_name(row),
                'description': self._parse_description(row),
                'classification': self._parse_classification(row),
                'start_time': dates['start'],
                'end_time': dates['end'],
                'all_day': self._parse_all_day(row),
                'timezone': 'America/Chicago',
                'status': self._parse_status(row),
                'location': self._parse_location(row),
            }
            data['id'] = self._generate_id(data, dates['start'])
            return data

        days = self._days_for_frequency(row[Row.FREQUENCY], row[Row.DAY_OF_WEEK])
        return [build_event(day) for day in days]

    def _parse_name(self, row):
        """
        Create event name
        """

        values = {
            'ward': row[Row.WARD],
            'alderman': row[Row.ALDERMAN],
        }
        name = 'Ward Night: Ward {ward}'.format(**values)
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
            'name': row[Row.ADDRESS].strip(),
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

        values = {
            'ward': row[Row.WARD],
            'alderman': row[Row.ALDERMAN],
        }
        template = 'Ward Night with Alderman {alderman} (Ward {ward}).\n'
        summary = template.format(**values)
        return summary + row[Row.INFO]

    def _parse_date_time(self, row, day):
        """
        Parse start-date-time and end-date-time
        """
        start_time = datetime.strptime(row[Row.START_TIME], '%I:%M %p')
        start_datetime = datetime.combine(day, start_time.time())

        end_time = datetime.strptime(row[Row.END_TIME], '%I:%M %p')
        end_datetime = datetime.combine(day, end_time.time())

        return {'start': self._naive_datetime_to_tz(start_datetime),
                'end': self._naive_datetime_to_tz(end_datetime)}
