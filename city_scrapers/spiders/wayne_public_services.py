# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import Wayne_commission


class Wayne_public_servicesSpider(Wayne_commission, Spider):
    name = 'wayne_public_services'
    agency_id = 'Wayne County Committee on Public Services'
    start_urls = ['https://www.waynecounty.com/elected/commission/public-services.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        entries = response.xpath('//tbody/tr')

        for item in entries:
            data = {
                '_type': 'event',
                'name': 'Committee on Public Services',
                'event_description': self._parse_description(item),
                'classification': 'Committee',
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(item, response.url),
                'sources': [{'url': response.url, 'note': ''}]
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')

            yield data

    @staticmethod
    def _parse_description(response):
        """
        Event description taken from static text at top of page.
        """
        desc_xpath = '//h2[contains(text(), "Public Services")]/following-sibling::div/section/p/text()'
        desc = response.xpath(desc_xpath).extract_first()
        return desc
