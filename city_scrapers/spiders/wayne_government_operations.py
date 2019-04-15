from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneGovernmentOperationsSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_government_operations'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/government-operations.aspx']
    meeting_name = 'Committee on Government Operations'
