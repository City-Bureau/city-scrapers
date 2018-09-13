# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime
import re

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiPoliceBoardSpider(Spider):
    name = 'chi_policeboard'
    timezone = 'America/Chicago',
    agency_name = 'Chicago Police Board Board of Directors'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['http://www.cityofchicago.org/city/en/depts/cpb/provdrs/public_meetings.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        data = {
            '_type': 'event',
            'name': self._parse_name(response),
            'event_description': self._parse_description(response),
            'classification': BOARD,
            'end': {'date': None, 'time': None, 'note': ''},
            'all_day': False,
            'location': self._parse_location(response),
            'sources': [{'url': response.url, 'note': ''}],
        }
        year = self._parse_year(response)
        start_time = self._parse_start_time(response)

        for item in response.xpath('//p[contains(@style,"padding-left")]'):
            start_date = self._parse_start_date(item, year)
            new_item = {
                'start': {
                    'date': start_date,
                    'time': start_time,
                    'note': '',
                },
                'documents': self._parse_documents(item, response),
            }
            new_item.update(data)
            new_item['id'] = self._generate_id(new_item)
            new_item['status'] = self._generate_status(new_item, '')
            yield new_item

    def _parse_documents(self, item, response):
        anchors = item.xpath('a')
        return [{'url': response.urljoin(link.xpath('@href').extract_first('')),
                 'note': link.xpath('text()').extract_first('')} for link in anchors]

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        bold_text = ' '.join(response.xpath("//strong/text()").extract())
        location_name = bold_text.split('take place at')[-1].split('.')[0].strip()
        return {
            'address': location_name,
            'name': None,
            'neighborhood': '',
        }

    def _parse_start_time(self, response):
        """
        Return start time
        """
        bold_text = ' '.join(response.xpath("//strong/text()").extract())
        match = re.match(r'.*(\d+:\d\d\s*[p|a]\.*m\.*).*', bold_text.lower())
        if match:
            cleaned_time = match.group(1).replace(' ', '').replace('.', '').upper()
            return datetime.strptime(cleaned_time, '%I:%M%p').time()
        return None

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        return response.css("h1[class='page-heading']::text").extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event name.
        """
        all_text = response.xpath(
            "normalize-space(//div[@class='container-fluid page-full-description'])").extract_first()

        intro, meetings = all_text.split('Regular Meetings')

        # Strip 5 characters ("2017 ") off end.
        return intro[:-5].strip()

    def _parse_start_date(self, item, year):
        """
        Parse start date
        """
        weekday_and_date = ''.join([x.strip() for x in item.xpath("text()").extract()])
        date = ''.join([x.strip() for x in weekday_and_date.split(',')[1:]])
        clean_date_match = re.match(r'.*([A-Z][a-z]+ \d+).*', date)
        if not clean_date_match:
            return None
        date_as_string = clean_date_match.group(1)
        date_with_year = '{0}, {1}'.format(date_as_string, year)
        return datetime.strptime(date_with_year, '%B %d, %Y').date()

    def _parse_year(self, response):
        """
        Look for a string of 4 numbers to be the year.
        If not found, use current year.
        """
        for entry in response.xpath('//h3/text()').extract():
            year_match = re.search(r'([0-9]{4})', entry)
            if year_match:
                return year_match.group(1)
