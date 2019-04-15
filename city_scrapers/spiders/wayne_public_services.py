from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WaynePublicServicesSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_public_services'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/public-services.aspx']
    meeting_name = 'Committee on Public Services'
