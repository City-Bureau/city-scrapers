# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

from datetime import datetime
from pytz import timezone


class CccSpider(scrapy.Spider):
    name = 'ccc'
    allowed_domains = ['http://www.ccc.edu/departments/Pages/Board-of-Trustees.aspx']
    start_urls = ['http://www.ccc.edu/departments/Pages/Board-of-Trustees.aspx']

    # for each link
    #   parse 
    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for link in response.css('a.Eventslink::attr(href)').extract():
            next_url = "http://www.ccc.edu" + link
            yield scrapy.Request(next_url, callback=self.parse_event_page, dont_filter=True)

    def parse_event_page(self, response):
            return {
                '_type': 'event',
                'id': self._parse_id(),
                'name': self._parse_name(response),
                'description': self._parse_description(response),
                'classification': self._parse_classification(),
                'start_time': self._parse_start(response),
                'end_time': self._parse_end(),
                'all_day': self._parse_all_day(),
                'status': self._parse_status(),
                'location': self._parse_location(),
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return None

    def _parse_id(self):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return None

    def _parse_classification(self):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': None,
            'coordinates': {
              'latitude': None,
              'longitude': None,
            },
        }

    def _parse_all_day(self):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        title = response.css('h1::text').extract_first()
        return title

    def _parse_description(self, response):
        """
        Parse or generate event name.
        """
        text_chunks = response.css('div.ms-rtestate-field::text').extract()

        return None

    def _parse_start(self, response):
        """
        Parse start date and time.
        """
        raw_date_time = response.css('div#formatDateA.required::text').extract_first()
        date_regex = r"(\d+)\/(\d+)\/(\d+)"
        time_regex = r"(\d+):(\d+)"

        tz = timezone('America/Chicago')

        d = re.search(date_regex, raw_date_time)
        t = re.search (time_regex, raw_date_time)

        naive_dt = datetime(month=int(d.group(1)), day=int(d.group(2)), year=int(d.group(3)), hour=int(t.group(1)), minute=int(t.group(2)))
        dt = tz.localize(naive_dt)
        return dt.isoformat()

    def _parse_end(self):
        """
        Parse end date and time.
        """
        return None
