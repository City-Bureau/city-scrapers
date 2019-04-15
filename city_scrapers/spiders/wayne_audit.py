from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneAuditSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_audit'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/audit.aspx']
    meeting_name = 'Audit Committee'
