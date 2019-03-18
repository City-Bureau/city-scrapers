from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetCityMixin


class DetHumanRightsSpider(DetCityMixin, CityScrapersSpider):
    name = 'det_human_rights'
    agency = 'Detroit Human Rights Commission'
    agency_cal_id = '1656'
    agency_doc_id = []  # No docs at time of creation

    def _parse_title(self, response):
        title = super()._parse_title(response)
        if 'meeting' in title.lower():
            return 'Human Rights Commission - Meeting'
        return 'Human Rights Commission'

    def _parse_description(self, response):
        return ''

    def _parse_classification(self, response):
        return COMMISSION
