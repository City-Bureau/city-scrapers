from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetTransportationSpider(DetCityMixin, CityScrapersSpider):
    name = "det_transportation"
    agency = "Detroit Department of Transportation"
    dept_cal_id = '166'
    agency_cal_id = 'All'
    dept_doc_id = '166'
    agency_doc_id = 'None'

    def _parse_classification(self, response):
        return BOARD
