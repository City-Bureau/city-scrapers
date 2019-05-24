from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetAuthorityMixin


class DetDowntownDevelopmentAuthoritySpider(DetAuthorityMixin, CityScrapersSpider):
    name = 'det_downtown_development_authority'
    agency = 'Detroit Downtown Development Authority'
    start_urls = ['http://www.degc.org/public-authorities/dda/']
    title = 'Board of Directors'
    classification = BOARD
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226'
    }
