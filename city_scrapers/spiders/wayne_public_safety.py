from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WaynePublicSafetySpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_public_safety'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/public-safety-judiciary.aspx']
    meeting_name = 'Committee on Public Safety, Judiciary, and Homeland Security'
