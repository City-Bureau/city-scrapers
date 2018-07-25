# -*- coding: utf-8 -*-
import re

import scrapy
from dateutil.parser import parse

from city_scrapers.spider import Spider


class DetPoliceDeptSpider(Spider):
    name = 'det_police_commissioners_board'
    agency_id = 'Police Department'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['http://www.detroitmi.gov/Calendar-Events']

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self._filter_category)

    def _filter_category(self, response):
        site_category_name = 'Board of Police Commissioners'
        category_dropdown = '//select[contains(@id, "select_category")]'
        link = './/option[contains(text(), "{}")]/@value'.format(site_category_name)
        category_url = response.xpath(category_dropdown).xpath(link).extract_first('')
        yield scrapy.Request(url=category_url, callback=self.parse)

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.news_post'):
            desc = self._parse_description(item)
            data = {
                '_type': 'event',
                'name': 'Board of Commissioners',
                'event_description': desc,
                'classification': 'Board',
                'start': self._parse_start(desc),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': self._parse_location(desc),
                'documents': [],
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    @staticmethod
    def _parse_description(item):
        desc = item.css('.post_content::text').extract()
        desc = [s.strip() for s in desc if s.strip()]
        desc = ' '.join(desc)
        return desc

    @staticmethod
    def _parse_start(item):
        time_regex = re.compile(r'((1[0-2]|0?[1-9])(:([0-5]?[0-9]))?( ?[AP]M))', re.IGNORECASE)
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        date_text = date_regex.search(item)
        time_text = time_regex.search(item)
        if date_text.lastindex >= 1 and time_text.lastindex >= 1:
            dt = parse(date_text.group(1) + " " + time_text.group(1), fuzzy=True)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        return {'date': None, 'time': None, 'note': ''}

    @staticmethod
    def _parse_location(item):
        address_text = re.split(r'(@|at)', item)[-1]
        if address_text.strip():
            return {'address': address_text.strip(), 'name': '', 'neighborhood': ''}
        return {'address': '', 'name': '', 'neighborhood': ''}
