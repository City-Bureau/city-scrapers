# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import os
import json
from datetime import datetime, timedelta
from enum import IntEnum
from pytz import timezone

from dateutil.rrule import rrule, MONTHLY, WEEKLY, MO, TU, WE, TH, FR, SA, SU

from city_scrapers.constants import COMMITTEE
from city_scrapers.spider import Spider

GOOGLE_API_KEY = os.environ.get('CITY_SCRAPERS_GOOGLE_API_KEY') or 'test-token'
SPREADSHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/1uzgWLWl19OUK6RhkAuqy6O6p4coTOqA22_nmKfzbakE'


class Row(IntEnum):
    """
    This enum makes working with the data rows more pleasant.
    """

    SCHOOL_ID = 0        # Text, "609924"
    AGENCY_NAME = 1      # Text, "Chicago Public Schools"
    NAME = 2             # Text, "Local School Council: Fort Dearborn ES"
    DATE = 3             # Date, "1/8/18"
    TIME = 4             # Time, "4:00:00 PM"
    SHORT_NAME = 5       # Text, "FORT DEARBORN"
    ADDRESS = 6          # Text, "9025 S Throop St"
    ZIP = 7              # Text, "60620"
    LAT = 8              # Text, "41.72967267"
    LONG = 9             # Text, "-87.65548116"
    PHONE = 10           # Text, "1(773)535-2680"
    COMMUNITY_AREA = 11  # Text, "Washington Heights"


class ChiLocalSchoolCouncilSpider(Spider):
    name = 'chi_localschoolcouncil'
    agency_name = 'Chicago Public Schools Local School Councils'
    timezone = 'America/Chicago'
    allowed_domains = ['sheets.googleapis.com/v4/']
    start_urls = [SPREADSHEET_URL + '/values/A2:L1400?key=' + GOOGLE_API_KEY]

    def __init__(self, start_date=datetime.today(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = start_date

    def parse(self, response):
        """
        Yields a dictionary with the required keys.
        """

        rows = json.loads(response.body.decode('utf-8'))['values']
        rows = [row for row in rows if (len(row) == 12)]
        now = self.start_date.replace(tzinfo=timezone(self.timezone))

        for row in rows:
            # Strip leading or trailing whitespace from all values
            for i in range(len(row)):
                row[i] = row[i].strip()

            # The JSON omits values for trailing columns with no values. By padding
            # the rows out, the rest of the code can assume there will always be 14
            # columns.
            missing_values = 13 - len(row)
            row.extend([''] * missing_values)
            data = self._parse_row(row)
            yield data

            # Only work with the next month's worth of meetings
            # to avoid overloading database
            delta = self._parse_start_datetime(row).replace(tzinfo=timezone(self.timezone)) - now
            if delta.days > 30 or delta.days < 0:
                yield None
            else:
                yield data

    def _parse_row(self, row):
        """
        Parse a row in the spreadsheet.
        """
        data = {
            '_type': 'event',
            'event_description': '',
            'classification': COMMITTEE,
            'all_day': False,
            'documents': [],
            'sources': self._parse_sources(),
            'name': self._parse_name(row),
            'start': self._parse_start(row),
            'end': self._parse_end(row),
            'location': self._parse_location(row)
        }
        data['id'] = self._generate_id(data)
        data['status'] = self._generate_status(data, '')
        return data

    def _parse_sources(self):
        """
        Return a URL to the google sheet as the source.
        """
        return [{
            'url': 'https://docs.google.com/spreadsheets/d/1uzgWLWl19OUK6RhkAuqy6O6p4coTOqA22_nmKfzbakE',
            'note': 'Google Sheet that Darryl filled out manually'
            }]

    def _parse_name(self, row):
        """
        Parse name from spreadsheet row.
        """
        return row[Row.NAME]

    def _parse_location(self, row):
        """
        Parse location from spreadsheet row.
        """
        return {
            'name': '',
            'address': "{} {}".format(row[Row.ADDRESS], row[Row.ZIP]),
            'neighborhood': row[Row.COMMUNITY_AREA]
        }

    def _parse_start_datetime(self, row):
        """
        Parse date and time values from spreadsheet row
        and returns a datetime object.
        """
        complete_datetime = "{} {}".format(row[Row.DATE], row[Row.TIME])
        return datetime.strptime(complete_datetime, '%m/%d/%y %I:%M:%S %p')

    def _parse_start(self, row):
        start_datetime = self._parse_start_datetime(row)
        return {
            'date': start_datetime.date(),
            'time': start_datetime.time(),
            'note': ''
        }

    def _parse_end(self, row):
        """
        Estimate the end time to be 3 hours after the start time.
        """
        start_datetime = self._parse_start_datetime(row)
        return {
            'date': start_datetime.date(),
            'time': (start_datetime + timedelta(hours=3)).time(),
            'note': 'estimated 3 hours after start time'
        }