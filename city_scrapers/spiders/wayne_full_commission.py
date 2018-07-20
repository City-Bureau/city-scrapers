# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import Wayne_commission


class Wayne_full_commissionSpider(Wayne_commission, Spider):
    name = 'wayne_full_commission'
    agency_id = 'Wayne County Full Commission'
    start_urls = ['https://www.waynecounty.com/elected/commission/full-commission.aspx']
    meeting_name = 'Wayne County Full Commission'

    # Override the mixin for any unique attributes.
    classification = 'Board'
    location = {
        'name': 'Mezzanine level, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    }

    @staticmethod
    def _parse_description(response):
        """
        @TODO Event description should be based on feedback from CB, since
        it also contains alternate location info.
        """
        desc = ("The vote on the final adoption of any resolution or "
                "ordinance is done within the meeting of the Wayne County "
                "Commission.")
        return desc
