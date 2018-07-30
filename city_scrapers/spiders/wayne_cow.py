# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import Wayne_commission


class Wayne_cowSpider(Wayne_commission, Spider):
    name = 'wayne_cow'
    agency_id = 'Detroit Committee of the Whole'
    start_urls = ['https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx']
    meeting_name = 'Wayne County Committee of the Whole'
