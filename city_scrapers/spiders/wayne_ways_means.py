from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneWaysMeansSpider(WayneCommissionMixin, CityScrapersSpider):
    name = 'wayne_ways_means'
    agency = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/ways-means.aspx']
    meeting_name = 'Ways and Means Committee'
