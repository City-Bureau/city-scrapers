# -*- coding: utf-8 -*-
from dateutil.parser import parse
from datetime import time
from urllib.parse import urljoin

import scrapy

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class DetZoningAppealsSpider(Spider):
    name = 'det_zoning_appeals'
    agency_name = 'Detroit Zoning Division Board of Zoning Appeals'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['https://www.detroitmi.gov/Government/Boards/Board-of-Zoning-Appeals-Meeting']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {
            'name': '13th Floor in the Auditorium, Coleman A. Young Municipal Center',
            'address': '2 Woodward Avenue, Detroit, MI 48226',
            'neighborhood': '',
        }
        for item in response.xpath('//td[contains(@class, "xl65")]/text()').extract():
            data = {
                '_type': 'event',
                'name': 'Board of Zoning Appeals',
                'event_description': '',
                'classification': BOARD,
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': location,
                'documents': self._parse_documents(response, item),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        try:
            meeting_date = parse(item)
            return {'date': meeting_date.date(), 'time': time(9, 00), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': item}

    def _parse_documents(self, response, item):
        """
        Parse or generate documents.
        """
        minutes_xpath = response.xpath('//div[contains(@id, "dnn_ctr7414_HtmlModule_lblContent")]//a')
        meeting_dates = self._parse_start(item)
        for minutes_item in minutes_xpath:
            minutes_date_text = minutes_item.xpath('text()').extract_first()
            minutes_date = parse(minutes_date_text)
            minutes_link = minutes_item.xpath('@href').extract_first()
            if minutes_date.date() == meeting_dates['date']:
                return [{'url': urljoin(response.url, minutes_link), 'note': 'Minutes'}]

        return []
