# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import os
import json
from datetime import datetime
from enum import IntEnum
from pytz import timezone

from dateutil.rrule import rrule, MONTHLY, WEEKLY, MO, TU, WE, TH, FR, SA, SU

from documenters_aggregator.spider import Spider

GOOGLE_API_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_GOOGLE_API_KEY') or 'test-token'
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

DESCRIPTION = """\
Every Chicago public school has a Local School Council (LSC) which consists of parents, community members, teachers, and the principal of the school. All members of the council are elected. which are responsible for three main duties: 1) Approving how school funds and resources are allocated 2) Developing and monitoring the annual School Improvement Plan 3) Evaluating and selecting the school's principal
"""

class chi_LSCMeetingSpider(Spider):
    name = 'chi_localschoolcouncil'
    long_name = 'Local School Council'
    allowed_domains = ['sheets.googleapis.com/v4/']
    start_urls = [SPREADSHEET_URL + '/values/A2:L1400?key=' + GOOGLE_API_KEY]

    def __init__(self, start_date=datetime.today(), *args, **kwargs):
        super(chi_LSCMeetingSpider, self).__init__(*args, **kwargs)
        self.start_date = start_date

    def parse(self, response):
        """
        Yields a dictionary with the required keys.
        """

        rows = json.loads(response.body.decode('utf-8'))['values']
        rows = [row for row in rows if (len(row) == 12)]
        now = datetime.now().replace(tzinfo=timezone('America/Chicago'))

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

            # Only work with the next month's worth of meetings
            # to avoid overloading Airtable
            delta = data['start_time'] - now
            if delta.days > 30 or delta.days < 0:
                yield None
            else:
                yield data

    def _parse_row(self, row):
        start_time = self._parse_start_time(row)

        complete_address = "{} {}".format(row[Row.ADDRESS], row[Row.ZIP])
        data = {
            '_type': 'event',
            'name': row[Row.NAME],
            'description': DESCRIPTION,
            'classification': 'meeting',
            'start_time': start_time,
            'end_time': None,
            'all_day': False,
            'timezone': 'America/Chicago',
            'status': 'tentative',
            'location': {
                'address': complete_address,
                'coordinates': {
                    'latitude': row[Row.LAT],
                    'longitude': row[Row.LONG],
                }
            }
        }
        data['id'] = self._generate_id(data, start_time)
        return data

    def _parse_start_time(self, row):
        """
        Parse date and time values from spreadsheet row.
        """
        complete_datetime = "{} {}".format(row[Row.DATE], row[Row.TIME])
        start_time = datetime.strptime(complete_datetime, '%m/%d/%y %I:%M:%S %p')


        return self._naive_datetime_to_tz(start_time)
