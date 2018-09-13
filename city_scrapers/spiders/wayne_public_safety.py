# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WaynePublicSafetySpider(WayneCommissionMixin, Spider):
    name = 'wayne_public_safety'
    agency_name = (
        'Wayne County Government Committee on Public Safety, '
        'Judiciary, and Homeland Security'
    )
    start_urls = ['https://www.waynecounty.com/elected/commission/public-safety-judiciary.aspx']
    meeting_name = (
        'Committee on Public Safety, Judiciary, and Homeland Security'
    )
