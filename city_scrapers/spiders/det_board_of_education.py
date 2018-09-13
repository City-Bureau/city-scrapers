# -*- coding: utf-8 -*-
import scrapy
from dateutil.parser import parse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class DetBoardOfEducationSpider(Spider):
    name = 'det_board_of_education'
    agency_name = 'Detroit Public Schools Board of Education'
    timezone = 'America/Detroit'
    allowed_domains = ['detroitk12.org']
    start_urls = ['http://detroitk12.org/board/meetings/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath('//h3[a]'):
            start, end = self._parse_start_end(item)
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': '',
                'classification': BOARD,
                'start': start,
                'end': end,
                'all_day': False,
                'location': self._parse_location(item),
                'documents': [],
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    @staticmethod
    def _parse_name(item):
        return item.xpath('a/text()').extract_first('')

    def _parse_start_end(self, item):
        # date text apparently just floats in main div
        # so get text after h3 meeting tag
        start_end_text = item.xpath('./following::text()[1]').extract_first()
        *date_text, time_text = start_end_text.split(' ', 3)
        date_text = ' '.join(date_text)
        start_time_text, end_time_text = time_text.split('–')
        start = self._create_meeting_time(date_text, start_time_text)
        end = self._create_meeting_time(date_text, end_time_text)
        return start, end

    @staticmethod
    def _create_meeting_time(date_text, time_text):
        meeting_dt = parse("{date} {time}".format(date=date_text, time=time_text))
        return {'date': meeting_dt.date(), 'time': meeting_dt.time(), 'note': ''}

    @staticmethod
    def _parse_location(item):
        address_xpath = './following-sibling::span[@class="address"][1]/text()'
        address = item.xpath(address_xpath).extract_first()
        return {'address': address, 'name': '', 'neighborhood': ''}
