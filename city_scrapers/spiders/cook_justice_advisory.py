import json
import re
import scrapy
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
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
        description = self._parse_description(response),
        classification=ADVISORY_COMMITTEE, 