# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

from datetime import datetime

class CplSpider(scrapy.Spider):
    name = 'cpl'
    allowed_domains = ['https://www.chipublib.org/']
    start_urls = ['https://www.chipublib.org/board-of-directors/board-meeting-schedule/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        events = response.css('div.entry-content p').extract()

        def cleanhtml(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        all_clean_events = []
        for val in events:
            clean_event = cleanhtml(val)
            final_event = clean_event.splitlines()
            all_clean_events.append(final_event)

        for item in response.css('.entry-content'):
            yield {
                '_type': 'event',
                'id': self._parse_id(item), #TODO
                'name': self._parse_name(item), #Chicago Public Library Board Meeting Schedule
                'description': self._parse_description(item),  #none ever on site
                'classification': self._parse_classification(item), #Board meeting?
                'start_time': self._parse_start(item), #turn date into correct format
                'end_time': self._parse_end(item), #no end time listed
                'all_day': self._parse_all_day(item), #default is false
                'status': self._parse_status(item), #?
                'location': self._parse_location(item), #2nd (and 3rd if it's 4 lines long) strings in event object
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return None
        #TODO: figure out unique ID-assigning mechanism

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

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        #s = response.css('strong::text').extract()
        #tz = timezone('America/Chicago')
        #TODO: turn every event array's first string into correct date format


    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return None
