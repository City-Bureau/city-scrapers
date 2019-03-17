from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetHistoricDistrictSpider(DetCityMixin, CityScrapersSpider):
    name = "det_historic_district"
    agency = "Detroit Historic District Commission"
    agency_cal_id = '1636'
    agency_doc_id = ['1636', '3776']

    def _parse_title(self, response):
        title = super()._parse_title(response)
        if 'regular' in title.lower():
            return 'Historic District Commission - Regular Meeting'
        return 'Historic District Commission'

    def _parse_description(self, response):
        return ""

    def _parse_classification(self, response):
        return COMMISSION
