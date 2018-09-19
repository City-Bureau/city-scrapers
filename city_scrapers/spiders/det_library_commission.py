# -*- coding: utf-8 -*-
import urllib.parse
from dateutil.parser import parse
import scrapy

from city_scrapers.constants import COMMISSION, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class DetLibraryCommissionSpider(Spider):
    name = 'det_library_commission'
    agency_name = 'Detroit Public Library'
    timezone = 'America/Detroit'
    allowed_domains = ['detroitpubliclibrary.org']
    start_urls = ['https://detroitpubliclibrary.org/about/commission']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        yield from self._generate_requests(response)

    def _generate_requests(self, response):
        anchor_xpath = '//div[contains(@class, "card-details")]/a'
        anchors = response.xpath(anchor_xpath)
        for a in anchors:
            yield response.follow(a, self._parse_item)

    def _parse_item(self, response):
        name = self._parse_name(response)
        location = self._get_location(response)
        classification = self._parse_classification(name)
        date, start_time, end_time = self._parse_date_and_times(response)
        data = {
            '_type': 'event',
            'name': name,
            'event_description': '',
            'classification': classification,
            'start': {
                'date': date,
                'time': start_time,
                'note': '',
            },
            'end': {
                'date': date,
                'time': end_time,
                'note': '',
            },
            'all_day': False,
            'location': location,
            'documents': [],
            'sources': [{'url': response.url, 'note': ''}],
        }
        data['id'] = self._generate_id(data)
        data['status'] = self._generate_status(data, text='')
        yield data

    @staticmethod
    def _parse_name(response):
        name_xpath = '//header/h1/text()'
        name = response.xpath(name_xpath).extract_first()
        return 'Library Commissioners: {}'.format(name)

    @staticmethod
    def _parse_classification(meeting_name):
        if 'Commission' in meeting_name:
            return COMMISSION
        return NOT_CLASSIFIED

    @staticmethod
    def _get_location(response):
        room_name = response.xpath('//td/small//text()').extract_first()
        branch_name = response.xpath('//td/strong//text()').extract_first()
        address_raw = response.xpath('substring-before(substring-after(//script[contains(.,"destination=")]/text(), "destination="), "U.S.")').extract_first()
        address_formatted = urllib.parse.unquote(address_raw).replace("\n", " ").strip()

        location = {
            'name': room_name + ', ' + branch_name + ' Branch' + ', Detroit Public Library',
            'address': address_formatted,
            'neighborhood': '',
        }
        return location

    @staticmethod
    def _parse_date_and_times(response):
        date_text = response.xpath('//tr[1]/td/text()').extract_first()
        time_text = response.xpath('//tr[2]/td/text()').extract_first()
        start_time, end_time = time_text.split(" - ")
        date_value = parse(date_text)
        start_value = parse(start_time)
        end_value = parse(end_time)

        return date_value.date(), start_value.time(), end_value.time()
