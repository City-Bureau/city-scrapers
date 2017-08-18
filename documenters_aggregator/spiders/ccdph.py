# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

from datetime import datetime, timedelta
from pytz import timezone
import time as Time

# @TODO:
# series event vs single event
# past events and repeats


class CcdphSpider(scrapy.Spider):
    name = 'ccdph'
    allowed_domains = ['http://www.cookcountypublichealth.org']
    start_urls = ['http://www.cookcountypublichealth.org/event-registration']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('div[class="event-item"] a::attr(href)').extract():
            next_url = self.allowed_domains[0] + '/' + item
            yield scrapy.Request(next_url, callback=self.parse_event_page,
                                 dont_filter=True)  # code doesn't work without this. idk why

    def parse_event_page(self, response):
        return {
            '_type': 'event',
            'id': self._parse_id(response),
            'name': self._parse_name(response),
            'description': self._parse_description(response),
            'classification': self._parse_classification(response),
            'start_time': self._parse_date_time(response)['start'],
            'end_time': self._parse_date_time(response)['end'],
            'all_day': self._parse_all_day(response),
            'status': self._parse_status(response),
            'location': self._parse_location(response),
        }

    def _parse_id(self, response):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return response.url.split('/')[-1]

    def _parse_classification(self, response):
        """
        Parse or generate classification (e.g. town hall).
        """
        name = response.css('td[valign="top"]  h3::text').extract_first()
        if name:
            return name.split(':')[0].strip()
        else:
            return None

    def _parse_status(self, response):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': response.xpath('//input[@type="hidden"][contains(@id, "Location")]/@value').extract_first(),
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        return response.css('td[valign="top"]  h3::text').extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event name.
        """
        descrip_list = response.css('div[id="tabDesc"] *::text').extract()
        description = ''.join([x.strip() for x in descrip_list])
        return description

    def _parse_date_time(self, response):
        """
        Parse start and end date and time
        """
        event_id = response.url.split('/')[-1]
        date_time_extract = response.xpath("//input[@value='{}']/parent::p/text()".format(event_id)).extract()
        date_time_str = ''.join([x.strip() for x in date_time_extract])

        match = re.search(r'Date:(.+);', date_time_str)
        if not match:
            return {'start': None, 'end': None}
        date = match.group(1).strip()

        match = re.search(r'Time:(.+)', date_time_str)
        if not match:
            return {'start': None, 'end': None}
        time = match.group(1).strip()
        start_time, end_time = [x.strip() for x in time.replace('.', '').upper().split('-')]

        start = self._make_date(date, start_time)
        end = self._make_date(date, end_time)
        return {'start': start, 'end': end}

    def _make_date(self, date, time):
            """
            Combine year, month, day with variable time and export as timezone-aware,
            ISO-formatted string.

            If date == 'Today', 'Tomorrow' or a day of the week like 'Friday',
            replace it with the date in month-day format
            """
            year = datetime.now().year
            if date == 'Today':
                date = datetime.now().strftime("%b %d")
            elif date == 'Tomorrow':
                tomorrow = datetime.now() + timedelta(days=1)
                date = tomorrow.strftime("%b %d")
            elif date.endswith('day'):
                today = datetime.today().weekday()
                date_integer = Time.strptime(date, "%A").tm_wday
                add_days = (date_integer - today) % 7
                date = datetime.now() + timedelta(days=add_days)
                date = date.strftime("%b %d")

            fmt_string = '{year} {date} {time}'
            time_string = fmt_string.format(year=year, date=date, time=time)

            naive = datetime.strptime(time_string, '%Y %b %d %I:%M %p')

            tz = timezone('America/Chicago')
            return tz.localize(naive).isoformat()
