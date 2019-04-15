from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneFullCommissionSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_full_commission'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/full-commission.aspx']
    meeting_name = 'Full Commission'

    # Override the mixin for any unique attributes.
    classification = BOARD
    location = {
        'name': 'Mezzanine level, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
    }
