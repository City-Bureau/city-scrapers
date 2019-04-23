from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetCharterReviewSpider(DetCityMixin, CityScrapersSpider):
    name = "det_charter_review"
    agency = "Detroit Charter Review Commission"
    agency_cal_id = "5621"
    agency_doc_id = "5621"

    def _parse_title(self, response):
        return "Charter Review Commission"

    def _parse_classification(self, response):
        description = self._parse_description(response)
        if "committee" in description.lower():
            return COMMITTEE
        return COMMISSION
