# -*- coding: utf-8 -*-
import re
from datetime import datetime

import scrapy
from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class ChiLowIncomeHousingTrustFundSpider(Spider):
    name = 'chi_low_income_housing_trust_fund'
    agency_name = 'Chicago Low-Income Housing Trust Fund'
    timezone = 'America/Chicago'
    allowed_domains = ['www.chicagotrustfund.org']
    start_urls = ['http://www.chicagotrustfund.org/about-us/upcomingevents/']
    custom_settings = {'ROBOTSTXT_OBEY': False}

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        items = self._parse_calendar(response)
        for item in items:
            req = scrapy.Request(
                item['sources'][0]['url'],
                callback=self._parse_detail,
                dont_filter=True,
            )
            req.meta['item'] = item
            yield req

        # Only go to the next page once, so if query parameters are set, exit
        if '?month' not in response.url:
            yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = response.css(
            '.calendar-next a::attr(href)'
        ).extract_first()
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_calendar(self, response):
        """Parse items on the main calendar page"""
        items = []
        for item in response.css('.day-with-date:not(.no-events)'):
            name = self._parse_name(item)
            description = self._parse_description(item)
            sources = self._parse_sources(item, response.url)
            items.append({
                '_type': 'event',
                'name': name,
                'event_description': description,
                'classification': self._parse_classification(name),
                'all_day': False,
                'documents': [],
                'sources': sources,
            })
        return items

    def _parse_detail(self, response):
        """Parse detail page for additional information"""
        data = {
            **response.meta.get('item', {}),
            **self._parse_start_end_time(response),
            'location': self._parse_location(response),
        }
        data['status'] = self._generate_status(data, text='')
        data['id'] = self._generate_id(data)
        return data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item.css('.event-title::text').extract_first()

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        return item.xpath(
            './/span[@class="event-content-break"]/following-sibling::text()'
        ).extract_first()

    def _parse_classification(self, name):
        """
        Parse or generate classification (e.g. board, committee, etc).
        """
        if 'board' in name.lower():
            return BOARD
        if 'committee' in name.lower():
            return COMMITTEE
        return NOT_CLASSIFIED

    def _parse_start_end_time(self, response):
        """
        Parse start date and time.
        """
        time_str = response.css(
            '.cc-panel .cc-block > span::text'
        ).extract_first()
        time_str = re.sub(r'\s+', ' ', time_str)
        date_str = re.search(r'(?<=day, ).*(?= fro)', time_str).group().strip()
        start_str = re.search(r'(?<=from ).*(?= to)', time_str).group().strip()
        end_str = re.search(r'(?<=to ).*(?= \w{3})', time_str).group().strip()
        dt = datetime.strptime(date_str, '%B %d, %Y').date()
        return {
            'start': {
                'date': dt,
                'time': datetime.strptime(start_str, '%I:%M %p').time(),
                'note': '',
            },
            'end': {
                'date': dt,
                'time': datetime.strptime(end_str, '%I:%M %p').time(),
                'note': '',
            }
        }

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        addr_sel = response.css(
            '.cc-panel .cc-block:nth-child(2) > span:nth-of-type(2)::text'
        )
        if not addr_sel:
            addr_sel = response.css(
                '#span_event_where_multiline p:first-of-type::text'
            )
        addr_lines = addr_sel.extract()
        return {
            'address': ' '.join([
                re.sub(r'\s+', ' ', line).strip() for line in addr_lines
            ]),
            'name': '',
            'neighborhood': '',
        }

    def _parse_sources(self, item, response_url):
        """
        Parse or generate sources.
        """
        item_link = item.css('.calnk > a::attr(href)').extract_first()
        if item_link:
            return [{'url': item_link, 'note': ''}]
        return [{'url': response_url, 'note': ''}]
