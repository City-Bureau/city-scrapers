# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime
from pytz import timezone
import re


class CpbSpider(scrapy.Spider):
    name = 'cpb'
    long_name = 'Chicago Police Board'
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
            'description': self._parse_description(response),
            'classification': self._parse_classification(response),
            'end_time': self._parse_end(response),
            'all_day': self._parse_all_day(response),
            'location': self._parse_location(response),
            'sources': self._parse_sources(response)
        }
        universal_start_time = self._parse_universal_start(response)

        for item in response.xpath('//p[contains(@style,"padding-left")]'):
            new_item = {
                'id': self._parse_id(item),
                'start_time': self._parse_start(item, universal_start_time)
            }
            new_item.update(data)
            new_item['status'] = self._parse_status(new_item['start_time'])
            yield new_item

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        Use start date
        """
        start_date = self._parse_start_date(item)
        item_id = 'CPB{0}'.format(start_date).replace(' ', '')
        return item_id

    def _parse_classification(self, response):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, start_time):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        if datetime.now().isoformat() > start_time:
            return 'passed'
        return 'tentative'

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        bold_text = ' '.join(response.xpath("//strong/text()").extract())
        location_name = bold_text.split('take place at')[-1].split('.')[0].strip()
        return {
            'url': None,
            'name': location_name,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_universal_start(self, response):
        """
        Return universal start time in the form %I:%M%p
        """
        bold_text = ' '.join(response.xpath("//strong/text()").extract())
        match = re.match(r'.*(\d+:\d\d\s*[p|a]\.*m\.*).*', bold_text.lower())
        if match:
            return match.group(1).replace(' ', '').replace('.', '').upper()
        return None

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        return response.css("h1[class='page-heading']::text").extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event name.
        """
        all_text = response.xpath("normalize-space(//div[@class='container-fluid page-full-description'])").extract_first()

        intro, meetings = all_text.split('Regular Meetings')

        # Strip 5 characters ("2017 ") off end.
        return intro[:-5].strip()

    def _parse_start(self, item, time):
        """
        Parse start date and time.
        """
        date = self._parse_start_date(item)
        year = str(datetime.now().year)
        datestring = '{0}, {1} {2}'.format(date, year, time)
        return self._make_date(datestring)

    def _parse_start_date(self, item):
        """
        Parse start date
        """
        weekday_and_date = ''.join([x.strip() for x in item.xpath("text()").extract()])
        date = ''.join([x.strip() for x in weekday_and_date.split(',')[1:]])
        clean_date_match = re.match(r'.*([A-Z][a-z]+ \d+).*', date)
        if not clean_date_match:
            return None
        return clean_date_match.group(1)

    def _make_date(self, datestring):
        """
        Combine year, month, day with variable time and export as timezone-aware,
        ISO-formatted string.
        """
        try:
            naive = datetime.strptime(datestring, '%B %d, %Y %I:%M%p')
        except ValueError:
            return None

        tz = timezone('America/Chicago')
        return tz.localize(naive).isoformat()

    def _parse_end(self, response):
        """
        Parse end date and time.
        """
        return None

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
