# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime


class ParksboardSpider(scrapy.Spider):
    name = 'parksboard'
    allowed_domains = ['chicagoparkdistrict.legistar.com']
    start_urls = ['https://chicagoparkdistrict.legistar.com/Calendar.aspx']
    domain_root = 'https://chicagoparkdistrict.legistar.com'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.rgRow,.rgAltRow'):
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item),
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
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        raw_cal_string = item.css('td:nth-child(3) a::attr(href)').extract_first()
        return raw_cal_string.split('&')[1].split('=')[1]

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

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
        Parse or generate location. Url, latitude and longitude are all
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

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item.css('td:nth-child(1) font::text').extract()[1]

    def _parse_description(self, item):
        """
        Parse or generate description name.
        """
        return None

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date = item.css('td:nth-child(2) font::text').extract_first()
        return date

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return None
