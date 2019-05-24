from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetAuthorityMixin


class DetEconomicDevelopmentCorporationSpider(DetAuthorityMixin, CityScrapersSpider):
    name = 'det_economic_development_corporation'
    agency = 'Detroit Economic Development Corporation'
    start_urls = ['http://www.degc.org/public-authorities/edc/']
    title = 'Board of Directors'
    classification = BOARD
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226'
    }
