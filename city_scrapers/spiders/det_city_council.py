import re

from city_scrapers_core.constants import CITY_COUNCIL, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetCityCouncilSpider(DetCityMixin, CityScrapersSpider):
    name = 'det_city_council'
    agency = 'Detroit City Council'
    agency_cal_id = '296'

    def parse_event_page(self, response):
        # Ignore districts, president if title not sufficient
        meeting = super().parse_event_page(response)
        tags = self._parse_tags(response)
        if (
            any(['District' in tag for tag in tags])
            or re.match(r'Coffee|Recess|District \d{1,2}', meeting['title'], flags=re.IGNORECASE)
        ):
            return
        return meeting

    def _parse_description(self, response):
        return ''

    def _parse_classification(self, response):
        if 'Committee' in self._parse_title(response):
            return COMMITTEE
        return CITY_COUNCIL

    def _parse_tags(self, response):
        return response.css('article.tags a::text').extract()
