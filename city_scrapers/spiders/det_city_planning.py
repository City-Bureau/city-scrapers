from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetCityPlanningSpider(DetCityMixin, CityScrapersSpider):
    name = 'det_city_planning'
    agency = 'Detroit City Planning Commission'
    agency_cal_id = '1591'
    agency_doc_id = ['3761', '5316']

    def _parse_title(self, response):
        title = super()._parse_title(response)
        if 'commission' not in title.lower():
            return title
        return 'City Planning Commission'

    def _parse_description(self, response):
        return ''

    def _parse_classification(self, response):
        return COMMISSION
