import json
import re
import scrapy
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookJusticeAdvisorySpider(CityScrapersSpider):
    name = 'cook_justice_advisory'
    agency = 'Cook County Justice Advisory'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cookcountyil.gov']

    def start_requests(self):
        toay = datetime.now()
        url = 'https://www.cookcountyil.gov/service/justice-advisory-council-meetings'
        yield scrapy.Request(url=url, method='GET', callback=self.parse)
        

    def parse(self, response):
       """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

    def _parse_event(self, response):
        """Parse the event page."""
        title = self._parse_title(response)
        meeting = Meeting(
            description = self._parse_description(response),
            classification=ADVISORY_COMMITTEE, 
            start=self._parse_start(response),
            end=self._parse_end(response),
            time_notes='',
            all_day=self._parse_all_day(response),
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting['id'] = self._get_id(meeting)
        meeting['status'] = self._get_status(meeting)
        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all board of ethics meetings on the page
        """
        
    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all optional and may e more trouble than they're worth to collect.
        """
    
    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """

    def _parse_title(self, reponse):
        """Parse or generate event"""

    def _parse_description(self, response):
        """Parse or generate event description."""

    def _parse_start(self, response):
        """Parse start date and time"""

    def _parse_end(self, response):
        """Parse end date and time"""
        
    def _parse_links(self, response):
        