# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import WayneCommissionMixin


class WayneFullCommissionSpider(WayneCommissionMixin, Spider):
    name = 'wayne_full_commission'
    agency_name = 'Wayne County Government'
    start_urls = ['https://www.waynecounty.com/elected/commission/full-commission.aspx']
    meeting_name = 'Full Commission'

    # Override the mixin for any unique attributes.
    classification = BOARD
    location = {
        'name': 'Mezzanine level, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    }
