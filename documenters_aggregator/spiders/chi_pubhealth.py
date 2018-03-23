# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import re
from datetime import datetime
from time import strptime

from documenters_aggregator.spider import Spider


class Chi_pubhealthSpider(Spider):

    name = 'chi_pubhealth'
    long_name = 'Chicago Department of Public Health'
    allowed_domains = ['www.cityofchicago.org']

    @property
    def start_urls(self):
        """
        DPH generally uses a standard URL format, but sometimes deviates from
        the pattern. This property inserts the current year into the standard
        format, as well as known variants, in hopes DPH sticks to one of their
        conventions and this scraper does not need to be updated annually.
        """
        standard_url = 'https://www.cityofchicago.org/city/en/depts/cdph/supp_info/boh/{}-board-of-health-meetings.html'
        url_variant_1 = 'https://www.cityofchicago.org/city/en/depts/cdph/supp_info/boh/{}-board-of-health.html'

        current_year = datetime.now().year

        return [
            standard_url.format(current_year),
            url_variant_1.format(current_year),
        ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        title = response.xpath('//h1[@class="page-heading"]/text()').extract_first()

        # Extract year and meeting name from title like "2017 Board of Health Meetings"
        parts = re.match(r'(\d{4}) (.*?)s', title)
        year = int(parts.group(1))
        name = parts.group(2)

        # The description and meeting dates are a series of p elements
        p = response.xpath('//div[contains(@class, "page-full-description-above")]/div/div/p')

        for idx, item in enumerate(p, start=1):

            if idx == 1:
                # Description is the first p element
                description = item.xpath('text()').extract_first()
                continue

            # Future meetings are plain text
            date_text = item.xpath('text()').extract_first()

            if not date_text:
                # Past meetings are links to the agenda
                date_text = item.xpath('a/text()').extract_first()

            # Extract date formatted like "January 12"
            date = datetime.strptime(date_text, '%B %d')

            naive_start_time = datetime(year, date.month, date.day, 9)
            start_time = self._naive_datetime_to_tz(naive_start_time)

            naive_end_time = datetime(year, date.month, date.day, 10, 30)
            end_time = self._naive_datetime_to_tz(naive_end_time)

            data = {
                '_type': 'event',
                'name': name,
                'description': description,
                'classification': self._parse_classification(item),
                'start_time': start_time,
                'end_time': end_time,
                'all_day': False,
                'timezone': 'America/Chicago',
                'status': self._parse_status(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data, start_time)
            yield data

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'committee-meeting'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        A lot of this info is hard coded as it is unlikely to frequently change.
        """
        return {
            'url': 'https://www.cityofchicago.org/city/en/depts/cdph.html',
            'name': '2nd Floor Board Room, DePaul Center',
            'address': '333 S. State Street, Chicago, IL',
            'coordinates': {
                'latitude': None,
                'longitude': None,
            }
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
