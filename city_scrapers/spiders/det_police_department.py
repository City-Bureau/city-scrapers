from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetPoliceDepartmentSpider(DetCityMixin, CityScrapersSpider):
    name = 'det_police_department'
    agency = 'Detroit Police Department'
    agency_cal_id = '1676'
    agency_doc_id = '5151'

    def _parse_title(self, response):
        return 'Board of Police Commissioners'

    def _parse_description(self, response):
        return ''

    def _parse_classification(self, response):
        return BOARD
