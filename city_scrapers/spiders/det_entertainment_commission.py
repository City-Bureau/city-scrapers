# -*- coding: utf-8 -*-
import re
from datetime import datetime, time
from dateutil.parser import parse

import scrapy

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class DetEntertainmentCommissionSpider(Spider):
    name = 'det_entertainment_commission'
    agency_name = 'Detroit Entertainment Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitsentertainmentcommission.com']
    start_urls = ['https://www.detroitsentertainmentcommission.com/services']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {
            'name': 'Coleman A. Young Municipal Center',
            'address': '2 Woodward Avenue, Detroit, MI 48226',
            'neighborhood': '',
        }

        for item in self._parse_entries(response):

            data = {
                '_type': 'event',
                'name': 'Entertainment Commission',
                'event_description': '',
                'classification': COMMISSION,
                'start': self._parse_start(item, response),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': location,
                'documents': [],
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_entries(self, response):
        entries_list = []
        month_day_xpath = response.xpath('//p[span[contains(string(), "Next Meeting Date")]]/following-sibling::p[span]//text()').extract()
        for item in month_day_xpath:
            valid_entry = re.match(r"\w+ \d{1,2}$", item)
            if valid_entry:
                entries_list.append(item)
        return entries_list

    def _parse_start(self, item, response):
        """
        Parse start date and time.
        """
        year_text = response.xpath('//p//span[contains(string(), "Meeting Dates")]/text()').extract_first()
        year_regex = re.search(r"(\d+){4}", year_text).group(0)
        try:
            start_date = parse(item + ', ' + year_regex)
            return {'date': start_date.date(), 'time': time(17, 00), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': item}
