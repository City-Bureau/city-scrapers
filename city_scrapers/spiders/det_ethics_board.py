from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider
from city_scrapers.mixins import DetCityMixin


class DetEthicsBoardSpider(DetCityMixin, CityScrapersSpider):
    name = "det_ethics_board"
    agency = "Detroit Board of Ethics"
    timezone = "America/Detroit"
    agency_cal_id = '1356'
    agency_doc_id = ['5116', '5101']


    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

