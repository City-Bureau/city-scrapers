from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetZoningAppealsSpider(DetCityMixin, CityScrapersSpider):
    name = 'det_zoning_appeals'
    agency = 'Detroit Board of Zoning Appeals'
    agency_cal_id = '1536'
    agency_doc_id = '3506'

    def _parse_title(self, response):
        if 'docket' in super()._parse_title(response).lower():
            return 'Board of Zoning Appeals - Docket'
        return 'Board of Zoning Appeals'

    def _parse_description(self, response):
        return ''

    def _parse_classification(self, response):
        return BOARD
