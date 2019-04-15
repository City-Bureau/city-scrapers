from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneCommitteeWholeSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_cow'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx']
    meeting_name = 'Committee of the Whole'
