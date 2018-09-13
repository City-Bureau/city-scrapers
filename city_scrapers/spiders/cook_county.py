# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
from urllib import parse

import scrapy

from datetime import datetime

from city_scrapers.constants import (
    ADVISORY_COMMITTEE, BOARD, COMMISSION, COMMITTEE, NOT_CLASSIFIED
)
from city_scrapers.spider import Spider


class CookCountySpider(Spider):
    name = 'cook_county'
    agency_name = 'Cook County Government'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cookcountyil.gov']
    url = 'https://www.cookcountyil.gov/calendar'
    # filter out non-governing events with query
    query = {
        "field_categories_tid_entityreference_filter[]": [
            "19",  # 19 = Board Meetings
            "205",  # 205 = Committee Meeting
            "20",  # 20 = Public Forum
            "206",  # 206 = Subcommittee Meeting
        ]
    }

    def start_requests(self):
        yield scrapy.FormRequest(url=self.url, method='GET', formdata=self.query, callback=self.parse)

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        for url in self._get_event_urls(response):
            next_url = 'https://{0}{1}'.format(self.allowed_domains[0], url)
            yield scrapy.Request(next_url, callback=self._parse_event, dont_filter=True)

        next_page = response.css('li.pager-next a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_event(self, response):
        """
        Parse the event page.
        """
        data = {
            '_type': 'event',
            'name': self._parse_name(response),
            'event_description': self._parse_description(response),
            'start': self._parse_start(response),
            'end': self._parse_end(response),
            'all_day': self._parse_all_day(response),
            'location': self._parse_location(response),
            'documents': self._parse_documents(response),
            'sources': self._parse_sources(response)
        }
        data['id'] = self._generate_id(data)
        data['status'] = self._generate_status(data, data['event_description'])
        data['classification'] = self._parse_classification(data['name'])
        return data

    def _get_event_urls(self, response):
        """
        Get urls for all events on the page.
        """
        event_urls = response.xpath('//div[@class="view-content"]//a/@href').extract()
        return list(set([x for x in event_urls if '/event/' in x and 'cancelled' not in x]))

    @staticmethod
    def _parse_classification(name):
        name = name.upper()
        if re.search(r'A(C|(DVISORY)) (COMMITTEE|COUNCIL)', name):
            return ADVISORY_COMMITTEE
        if 'BOARD' in name:
            return BOARD
        if 'COMMITTEE' in name:
            return COMMITTEE
        if 'COMMISSION' in name:
            return COMMISSION
        return NOT_CLASSIFIED

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        address = response.xpath('//div[@class="field event-location"]/descendant::*/text()').extract()
        address = ' '.join([x.strip() for x in address])
        address = address.replace('Location:', '').strip()
        return {
            'neighborhood': None,
            'address': address,
            'name': None,
        }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()').extract()
        date = ''.join(date).upper()
        return 'ALL DAY' in date

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        return response.xpath('//h1/text()').extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event description.
        """
        category_field = response.xpath("//div[contains(., 'Category:') and contains(@class, 'field-label')]")
        field_items = category_field.xpath("./following::div[contains(@class, 'field-items')]")
        return ' '.join(
            field_items.xpath('.//p/text()').extract() +
            field_items.xpath('.//strong/text()').extract()
        ).strip()

    def _parse_start(self, response):
        """
        Parse start date and time.
        """
        start = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()').extract()
        start = ''.join(start).upper()
        start = start.split(' TO ')[0].strip()
        start = start.replace('(ALL DAY)', '12:00AM')

        dt = datetime.strptime(start, '%B %d, %Y %I:%M%p')
        return {'date': dt.date(), 'time': dt.time(), 'note': ''}

    def _parse_end(self, response):
        """
        Parse end date and time.
        """
        date = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()').extract()
        date = ''.join(date).upper()
        date.replace('(ALL DAY)', 'TO 11:59PM')
        start_end = date.split(' TO ')

        if len(start_end) < 2:
            return {'date': None, 'time': None, 'note': ''}

        end_time = start_end[1]
        date = start_end[0][:start_end[0].rindex(' ')]
        end = '{0} {1}'.format(date, end_time)
        naive = datetime.strptime(end, '%B %d, %Y %I:%M%p')
        return {'date': naive.date(), 'time': naive.time(), 'note': ''}

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]

    def _parse_documents(self, response):
        files = response.css('span.file a')
        return [{'url': f.xpath('./@href').extract_first(),
                 'note': f.xpath('./text()').extract_first()} for f in files]
