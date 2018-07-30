# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import re
from datetime import date, time, datetime
from time import strptime

from city_scrapers.spider import Spider


class Chi_pubhealthSpider(Spider):

    name = 'chi_pubhealth'
    agency_id = 'Chicago Department of Public Health'
    allowed_domains = ['www.cityofchicago.org']
    timezone = 'America/Chicago'

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
        self.year = int(parts.group(1))
        name = parts.group(2)

        # The description and meeting dates are a series of p elements
        p = response.xpath('//div[contains(@class, "page-full-description-above")]/div/div/p')

        for idx, item in enumerate(p, start=1):

            if idx == 1:
                # Description is the first p element
                description = item.xpath('text()').extract_first()
                continue

            data = {
                '_type': 'event',
                'name': name,
                'event_description': description,
                'classification': self._parse_classification(item),
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': False,
                'location': self._parse_location(item),
                'sources': self._parse_sources(response),
                'documents': self._parse_documents(item)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')
            yield data

    def _parse_date(self, item):
        """
        Parse the meeting date.
        """
        # Future meetings are plain text
        date_text = item.xpath('text()').extract_first()

        if not date_text:
            # Past meetings are links to the agenda
            date_text = item.xpath('a/text()').extract_first()
        
        # Extract date formatted like "January 12"
        return datetime.strptime(date_text, '%B %d')

    def _parse_start(self, item):
        """
        Parse the meeting date and set start time to 9am.
        """
        datetime_obj = self._parse_date(item)
        return {
            'date': date(self.year, datetime_obj.month, datetime_obj.day),
            'time': time(9, 0),
            'note': ''
        }

    def _parse_end(self, item):
        """
        Parse the meeting date and set end time to 10:30am.
        """
        datetime_obj = self._parse_date(item)
        return {
            'date': date(self.year, datetime_obj.month, datetime_obj.day),
            'time': time(10, 30),
            'note': ''
        }

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'board meeting'

    def _parse_location(self, item):
        """
        A lot of this info is hard coded as it is unlikely to frequently change.
        """
        return {
            'name': '2nd Floor Board Room, DePaul Center',
            'address': '333 S. State Street, Chicago, IL',
            'neighborhood': 'Loop'
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

    def _parse_documents(self, item):
        """
        Parse agenda and minutes, if available.
        """
        documents = []

        agenda_relative_url = item.xpath('a/@href').extract_first()
        if agenda_relative_url:
            documents.append({
                'url': 'https://www.cityofchicago.org{}'.format(agenda_relative_url),
                'note': 'agenda'
            })
        
        minutes_relative_url = item.xpath('following-sibling::ul/li/a/@href').extract_first()
        if agenda_relative_url:
            documents.append({
                'url': 'https://www.cityofchicago.org{}'.format(minutes_relative_url),
                'note': 'minutes'
            })
        return documents

