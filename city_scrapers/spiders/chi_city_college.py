# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
from datetime import datetime, timedelta

import scrapy

from city_scrapers.constants import BOARD, COMMITTEE
from city_scrapers.spider import Spider


class ChiCityCollegeSpider(Spider):
    name = 'chi_city_college'
    agency_name = 'City Colleges of Chicago'
    allowed_domains = ['www.ccc.edu']

    start_urls = [
        'http://www.ccc.edu/events/Pages/default.aspx?dept=Office%20of%20'
        'the%20Board%20of%20Trustees'
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for link in response.css('.event-entry .event-title a::attr(href)').extract():
            next_url = "http://www.ccc.edu" + link
            yield scrapy.Request(next_url, callback=self.parse_event_page, dont_filter=True)

    def parse_event_page(self, response):
        date_str = response.css('#formatDateA::text').extract_first()
        description = self._parse_description(response)
        for item in response.css('.page-content table tr'):
            start = self._parse_start(item, date_str)
            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'event_description': description,
                'classification': self._parse_classification(name),
                'start': {
                    'date': start.date(),
                    'time': start.time(),
                    'note': None,
                },
                'end': {
                    'date': start.date(),
                    'time': (start + timedelta(hours=2)).time(),
                    'note': 'Estimated 2 hours after start time',
                },
                'all_day': False,
                'location': self._parse_location(response),
                'documents': self._parse_documents(response),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data)
            yield data

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        # Default to Harold Washington College
        default_location = {
            'name': 'Harold Washington College',
            'address': '30 E. Lake Street Chicago, IL 60601',
            'neighborhood': None,
        }
        text = response.css(
            '#ctl00_PlaceHolderMain_FullDescription__'
            'ControlWrapper_RichHtmlField span::text'
        ).extract_first()
        if not text:
            return default_location

        match = re.search(r'\.m\.,([^,]+),(.+)', text)
        if match is not None:
            return {
                'name': match.group(1).strip(),
                'address': match.group(2).strip().rstrip('.'),
                'neighborhood': None,
            }
        else:
            return default_location

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        name = item.css('th:nth-child(2) ::text, td:nth-child(2) ::text').extract_first()
        if 'regular board meeting' in name.lower():
            return 'Board of Trustees'
        return name.replace('\u200b', '').strip()

    def _parse_description(self, response):
        content = response.css('.page-content > div:not([style="display:none"]) *::text')
        description = (' '.join([el.extract().strip() for el in [content[0], content[-1]]])).strip()
        return re.sub(r'\s+', ' ', description.replace('\u200b', '')).strip()

    def _parse_start(self, item, date_str):
        """Parse start date and time from item and page date string"""
        # Remove day of week if present
        date_str = re.search(r'[\d/]{8,10}', date_str).group()
        time_str = item.css('th::text, td::text').extract_first().replace('.', '')
        time_str = time_str.replace('noon', 'pm').replace('\u200b', '').strip()
        return datetime.strptime('{} {}'.format(date_str, time_str), '%m/%d/%Y %I:%M %p')

    def _parse_classification(self, name):
        if 'committee' in name.lower():
            return COMMITTEE
        return BOARD

    def _parse_documents(self, response):
        """Returns an array of documents if available"""
        documents = []
        document_links = response.xpath(
            "//div[contains(@class, 'right-col-block')]/h2[text() = 'Learn More']"
            "/following-sibling::*//a"
        )
        for doc_link in document_links:
            documents.append({
                'url': response.urljoin(doc_link.attrib['href']),
                'note': doc_link.xpath('./text()').extract_first(),
            })
        return documents

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
