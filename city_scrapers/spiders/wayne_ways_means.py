# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneWaysMeansSpider(WayneCommissionMixin, Spider):
    name = 'wayne_ways_means'
    agency_name = 'Wayne County Government Ways and Means Committee'
    start_urls = ['https://www.waynecounty.com/elected/commission/ways-means.aspx']
    meeting_name = 'Ways and Means Committee'
