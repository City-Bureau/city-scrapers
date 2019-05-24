from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetAuthorityMixin


class DetNeighborhoodDevelopmentCorporationSpider(DetAuthorityMixin, CityScrapersSpider):
    name = 'det_neighborhood_development_corporation'
    agency = 'Detroit Neighborhood Development Corporation'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/ndc/']
    title = 'Board of Directors'
    classification = BOARD
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226',
    }
