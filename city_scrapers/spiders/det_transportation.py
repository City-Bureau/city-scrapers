from city_scrapers_core.constants import BOARD, ADVISORY_COMMITTEE, FORUM
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
        event_title = super()._parse_title(response).lower()
        if ('input meeting' in event_title):
            return FORUM
        elif ('advisory council' in event_title):
            return ADVISORY_COMMITTEE
        else:
            return BOARD

    def parse_event_page(self, response):
        try:
            self._parse_start(response)
        except AttributeError:
            return
        return super().parse_event_page(response)
