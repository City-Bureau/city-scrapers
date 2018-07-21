# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

import re
from datetime import datetime
from dateutil.parser import parse as dateparse
from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import Wayne_commission


class Wayne_building_authoritySpider(Wayne_commission, Spider):
    name = 'wayne_building_authority'
    agency_id = 'Wayne County Building Authority'
    start_urls = ['https://www.waynecounty.com/boards/buildingauthority/meetings.aspx']
    meeting_name = 'Wayne County Building Authority'

    # Override the mixin for any unique attributes.
    location = {
        'name': '6th Floor, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    }

    def _parse_entries(self, response):
        # There are several tables with old meetings. Look for the current year
        # and get all rows which have children that contain text.
        current_year = datetime.now().year
        return response.xpath('//section[contains(.,"%s")]//tbody/tr[child::td/text()]' %current_year)

    @staticmethod
    def _parse_description(response):
        """
        Event description
        """
        desc = ("The County of Wayne will provide necessary reasonable "
                "auxiliary aids and services to individuals with disabilities "
                "at the meeting upon five days notice to the Legal Clerk of "
                "the Authority, such as signers for the hearing impaired and "
                "audio tapes of printed materials being considered at the "
                "meetings. Individuals with disabilities requiring "
                "auxiliary aids or services should contact the Authority in "
                "writing or call Audricka Grandison at (313) 967-1030.")
        return desc

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Strong text indicates the a replacement meeting date
        strong_text = item.xpath('.//td[2]/strong/text()').extract_first()
        if strong_text is not None:
            date_str = strong_text
        else:
            date_str = item.xpath('.//td[2]/text()').extract_first()

        time_str = item.xpath('.//td[3]/text()').extract_first()
        date_time_str = dateparse('{0} {1}'.format(date_str, time_str))

        return {'date': date_time_str.date(), 'time': date_time_str.time(), 'note': ''}

    def _parse_status(self, item, data):
        """
        Parse or generate status of meeting.
        Postponed meetings all have replacement dates which we account for in
        the _parse_start method.
        """

        # Our status may be buried inside a number of other elements
        status_str = item.xpath('.//td[4]/*/text() | .//td[4]/*/*/text() | .//td[4]/text()').extract_first()
        # Meetings that are truly cancelled will be marked here.
        if re.search(r'cancel', status_str, re.IGNORECASE):
            return 'cancelled'
        # If it's not cancelled, use the status logic from spider.py
        else:
            return self._generate_status(data, '')
