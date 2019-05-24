from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetAuthorityMixin


class DetLocalDevelopmentFinanceAuthoritySpider(DetAuthorityMixin, CityScrapersSpider):
    name = 'det_local_development_finance_authority'
    agency = 'Detroit Local Development Finance Authority'
    start_urls = ['http://www.degc.org/public-authorities/ldfa/']
    title = 'Board of Directors'
    classification = BOARD
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226'
    }
