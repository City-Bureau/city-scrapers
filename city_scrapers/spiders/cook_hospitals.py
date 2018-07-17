# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.parser import parse
from city_scrapers.spider import Spider


class Cook_hospitalsSpider(Spider):
    name = 'cook_hospitals'
    agency_id = 'Cook County Health and Hospitals System'
    timezone = 'America/Chicago'

    long_name = 'Cook County Health and Hospitals System'
    allowed_domains = ['www.cookcountyhhs.org']
    start_urls = ['http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/']
    domain_root = 'http://www.cookcountyhhs.org'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.
        """
        for item in response.xpath("//a[@class='h2 accordion-toggle collapsed']"):
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'all_day': False,
                'sources': [{'url': response.url, 'note': ''}],
            }

            aria_control = item.xpath("@aria-controls").extract_first()
            item_uncollapsed = item.xpath(
                "//div[@id='{}']//tbody//td[@data-title='Meeting Information']".format(aria_control))
            for subitem in item_uncollapsed:
                new_item = {
                    # TODO unsure where this should come from
                    'event_description': self._parse_description(subitem),
                    'location': self._parse_location(subitem),
                    'documents': self._parse_documents(subitem)
                }
                new_item.update(data)
                new_item.update(self._parse_times(subitem))
                new_item['status'] = self._generate_status(new_item, '')
                new_item['id'] = self._generate_id(new_item)
                new_item['classification'] = self._parse_classification(new_item['name'])
                yield new_item

    @staticmethod
    def _parse_classification(name):
        if 'BOARD' in name.upper():
            return 'Board'
        return 'Committee'

    @staticmethod
    def _parse_documents(subitem):
        anchors = subitem.xpath("following-sibling::td//a")
        documents = []
        if anchors:
            for a in anchors:
                documents.append({
                    'url': a.xpath('@href').extract_first(default=''),
                    'note': a.xpath('text()').extract_first(default='').lower()
                })
        return documents

    @staticmethod
    def _parse_location(subitem):
        """
        Parse location
        """
        address = subitem.xpath('text()').extract()[1]
        return {
            'address': address.strip(),
            'name': '',
            'neighborhood': '',
        }

    @staticmethod
    def _parse_name(item):
        """
        Get event name from item's text
        """
        return item.xpath('text()').extract_first().strip()

    @staticmethod
    def _parse_description(subitem):
        """
        Get url to agenda
        """
        return ''

    @staticmethod
    def _parse_times(subitem):
        """
        Combine start time with year, month, and day.
        """
        tokens = subitem.xpath('text()').extract_first().strip().split(' - ')
        date = parse(tokens[0])
        time = parse(tokens[1])
        times = {
            'start': {
                'date': date.date(),
                'time': time.time(),
                'note': ''
            },
            'end' : {
                'date': date.date()
            }
        }

        if len(tokens) > 2:
            times['end']['time'] = parse(tokens[2]).time()
            times['end']['note'] = ''
        else:
            times['end']['time'] = (time + timedelta(hours=3)).time()
            times['end']['note'] = 'End time is estimated to be 3 hours after the start time'

        return times
