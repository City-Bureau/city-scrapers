# -*- coding: utf-8 -*-
import scrapy

import re
from datetime import datetime

from city_scrapers.constants import (
    ADVISORY_COMMITTEE, BOARD, COMMITTEE, NOT_CLASSIFIED
)
from city_scrapers.spider import Spider


# The RTA's Board and other meetings are are displayed on their
# website via an iframe from a different domain.
class IlRegionalTransitSpider(Spider):
    name = 'il_regional_transit'
    agency_name = 'Regional Transportation Authority'
    timezone = 'America/Chicago'

    allowed_domains = ['www.rtachicago.org', 'rtachicago.granicus.com']
    start_urls = ['http://www.rtachicago.org/about-us/board-meetings']
    domain_root = 'http://www.rtachicago.org'

    def parse_iframe(self, response):
        for item in response.css('.committee'):
            start = self._parse_start(item)
            if start is None:
                continue
            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'event_description': response.meta['event_description'],
                'start': start,
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'timezone': 'America/Chicago',
                'location': self._parse_location(),
                'documents': self._parse_documents(item),
                'sources': [{'url': response.url, 'note': ''}],
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')
            data['classification'] = self._parse_classification(
                data.get('name', NOT_CLASSIFIED)
            )
            yield data

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard http://docs.opencivicdata.org/en/latest/data/event.html
        """
        url = response.css('iframe::attr(src)').extract_first()
        desc_xpath = '//*[text()[contains(.,"The RTA Board")]]/text()'
        description = response.xpath(desc_xpath).extract_first()
        meta = {
            'event_description': description,
            # Disable built-in RobotsTxt middleware for this request.
            'dont_obey_robotstxt': True,
        }
        yield scrapy.Request(url, callback=self.parse_iframe, meta=meta)

    @staticmethod
    def _parse_classification(name):
        name = name.upper()
        if 'CITIZENS ADVISORY' in name:
            return ADVISORY_COMMITTEE
        if 'COMMITTEE' in name:
            return COMMITTEE
        if 'BOARD' in name:
            return BOARD
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_location():
        """
        The location is hard coded based on the value shown on the meetings
        page. It is not expected to change often, so this is probably OK.
        """
        return {
            'name': 'RTA Administrative Offices',
            'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604',
        }

    @staticmethod
    def _parse_name(item):
        """
        Get event name
        """
        title = item.css('.committee::text').extract_first()
        return title.split(' on ')[0]

    @staticmethod
    def _parse_start(item):
        """
        Retrieve the event date, always using 8:30am as the time.
        """
        title = item.css('.committee::text').extract_first()
        m = re.search('(\d{4})-(\d{1,2})-(\d{1,2})', title)
        if m is None:
            return None
        naive_dt = datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)), 8, 30
        )
        return {
            'date': naive_dt.date(),
            'time': naive_dt.time(),
            'note': ''
        }

    @staticmethod
    def _parse_documents(item):
        document_xpath = 'ancestor::div[contains(@class, "row")]//a/@href'
        document = item.xpath(document_xpath).extract_first()
        if document:
            return [{'url': document, 'note': 'agenda'}]
        return []
