# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime


class CtpfSpider(scrapy.Spider):
    name = 'ctpf'
    allowed_domains = ['http://www.ctpf.org']
    start_urls = ['http://www.ctpf.org/general_info/boardmeetings.htm']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # response.xpath("//h4 | //p[@class='italics']"):
        # print
        # import pdb; pdb.set_trace()
        for item in response.css('#content'):
            name = item.response.xpath('//h4').replace('Schedule').strip()
            time_location = item.response.xpath('//h4/following-sibling::p[1]').replace('All meetings are held at', 'in the', 'unless otherwise noted.').strip()

            for item in response.xpath("//p[not(@class)]"):
                date = item.extract()

            yield {
                '_type': 'event',
                'id': self._parse_id(item), # todo
                'name': name,
                'description': self._parse_description(item), # todo?
                'classification': self._parse_classification(item), # todo?
                'start_time': self._parse_start(date, time_location),
                'end_time': False,
                'all_day': False,
                'status': self._parse_status(item),
                'location': self._parse_location(time_location), # todo
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
        return None

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

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_start(self, date, time_location):
        """
        Parse start date and time.
        """
        return time_location

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return None
