# -*- coding: utf-8 -*-
import datetime
import re

import scrapy

from city_scrapers.constants import ADVISORY_COMMITTEE
from city_scrapers.spider import Spider


class ChiMayorsBicycleAdvisoryCouncilSpider(Spider):
    name = 'chi_mayors_bicycle_advisory_council'
    agency_name = "Mayor's Bicycle Advisory Council"
    timezone = 'America/Chicago'
    allowed_domains = ['chicagocompletestreets.org']
    start_urls = ['http://chicagocompletestreets.org/getinvolved/mayors-advisory-councils/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        header, = response.xpath('//p[strong/span[contains(text(), "MBAC meeting dates")]]')
        self.year = self._parse_year(header)
        dates = header.xpath('following-sibling::p/text()')

        for date in dates.extract():
            date = date.replace('\xa0', ' ').replace('\n', '')

            if date.strip():
                date_with_year = '{date}, {year}'.format(date=date, year=self.year)

                data = {
                    '_type': 'event',
                    'name': self._parse_name(),
                    'event_description': self._parse_description(),
                    'classification': self._parse_classification(),
                    'start': self._parse_start(date_with_year),
                    'end': self._parse_end(date_with_year),
                    'all_day': self._parse_all_day(),
                    'location': self._parse_location(),
                    'documents': self._parse_documents(),
                    'sources': self._parse_sources(),
                }

                '''
                TO-DO: Determine whether defaulting to tentative (because there
                is never an agenda) is the correct thing to do. The site is
                slightly ambiguous about how deviations from the schedule will
                be reported, e.g., "meetings are _generally_ at such and such
                time."
                '''
                data['status'] = self._generate_status(data, text='')
                data['id'] = self._generate_id(data)

                yield data

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        pass

    def _parse_name(self):
        """
        Parse or generate event name.
        """
        return "Mayor's Bicycle Advisory Council"

    def _parse_description(self):
        """
        Parse or generate event description.
        """
        return 'MBAC focuses on a wide range of bicycle issues: safety, ' + \
            'education, enforcement, and infrastructure investment. The Council ' + \
            'will help identify issues, discuss ideas and set priorities for ' + \
            'bicycle planning in Chicago.'

    def _parse_classification(self):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return ADVISORY_COMMITTEE

    def _parse_year(self, header):
        '''
        Dates are not listed with a year. Grab it from the date listing header,
        e.g., "The 2018 MBAC meeting dates:"
        '''
        header_text, = header.xpath('strong/span/text()').extract()

        return re.search(r'\d{4}', header_text).group(0)

    def _parse_start(self, item):
        """
        Parse start date and time like "Wednesday, March 7, 2017."
        """
        date = datetime.datetime.strptime(item, '%A, %B %d, %Y').date()

        return {
            'date': date,
            'time': datetime.time(15, 0),
            'note': 'Start at 3 p.m. unless otherwise noted'
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        date = datetime.datetime.strptime(item, '%A, %B %d, %Y').date()

        return {
            'date': date,
            'time': None,
            'note': ''
        }

    def _parse_all_day(self):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': '121 N LaSalle Dr, Chicago, IL',
            'name': 'City Hall, Room 1103',
            'neighborhood': 'Loop',
        }

    def _parse_documents(self):
        """
        Parse or generate documents.
        """
        return []

    def _parse_sources(self):
        """
        Parse or generate sources.
        """
        return [{'url': self.start_urls[0], 'note': ''}]
