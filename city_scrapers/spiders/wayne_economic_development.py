from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneEconomicDevelopmentSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_economic_development'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/economic-development.aspx']
    meeting_name = 'Committee on Economic Development'
