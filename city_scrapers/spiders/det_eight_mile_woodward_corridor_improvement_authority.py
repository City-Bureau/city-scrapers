from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetAuthorityMixin


class DetEightMileWoodwardCorridorImprovementAuthoritySpider(DetAuthorityMixin, CityScrapersSpider):
    name = 'det_eight_mile_woodward_corridor_improvement_authority'
    agency = 'Detroit Eight Mile Woodward Corridor Improvement Authority'
    start_urls = ['http://www.degc.org/public-authorities/emwcia/']
    title = 'Board of Directors'
    classification = BOARD
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226',
    }
