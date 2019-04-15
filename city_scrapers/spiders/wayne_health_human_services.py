from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneHealthHumanServicesSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_health_human_services'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/health-human-services.aspx']
    meeting_name = 'Committee on Health and Human Services'
