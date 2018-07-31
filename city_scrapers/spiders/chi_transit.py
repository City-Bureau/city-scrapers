# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re

from datetime import datetime, timedelta
from pytz import timezone
from city_scrapers.spider import Spider



class ChiTransitSpider(Spider):
    name = 'chi_transit'
    agency_id = 'Chicago Transit Authority'
    timezone = 'America/Chicago'
    allowed_domains = ['www.transitchicago.com']
    base_url = 'http://www.transitchicago.com'
    start_urls = ['https://www.transitchicago.com/board/notices-agendas-minutes/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        today = datetime.now()
        response_items = response.css('.agendaminuteDataTbl tr:not(:first-child)')
        for idx, item in enumerate(response_items):
            # Including previous item for meetings where it's needed
            prev_item = response_items[idx - 1] if idx > 0 else None
            start_datetime = self._parse_start_datetime(item, prev_item)
            if start_datetime: #and today < start_datetime:
                item_data = {
                    '_type': 'event',
                    'name': self._parse_name(item),
                    'event_description': self._parse_description(item),
                    'classification': self._parse_classification(item),
                    'start': self._parse_start(item, prev_item),
                    'end': self._parse_end(item, prev_item),
                    'all_day': self._parse_all_day(item),
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(response),
                    'documents': self._parse_documents(item)
                }
                item_data['id'] = self._generate_id(item_data)
                item_data['status'] = self._generate_status(item_data, item_data['name'])
                yield item_data

    def _parse_description(self, item):
        return ''

    def _parse_all_day(self, item):
        return False

    def _parse_classification(self, item):
        """
        Classify meeting as board or committee meetings.
        """
        name = item.css('td:nth-child(3)::text').extract_first().lower()
        if 'board' in name:
            return 'board meeting'
        else:
            return 'committee meeting'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        location_str = item.css('td:nth-child(4)::text').extract_first()
        # Always 537 W Lake, so handle that if provided (but allow for change)
        if re.search(r'567 (W.|W|West) Lake.*|board\s?room', location_str, re.IGNORECASE) \
            or re.search(r'cta.*board.*room', location_str, re.IGNORECASE):
            return {
                'neighborhood': 'west loop',
                'name': 'Chicago Transit Authority 2nd Floor Boardroom',
                'address': '567 West Lake Street Chicago, IL',
            }
        else:
            return {
                'neighborhood': '',
                'name': '',
                'address': location_str,
            }

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item.css('td:nth-child(3)::text').extract_first()

    def _parse_documents(self, item):
        """
        Add meeting notice and agenda to documents
        """
        documents = []
        link_items = item.css('td:last-child a')
        for link in link_items:
            documents.append({
                'url': self.base_url + link.xpath('./@href').extract_first(),
                'note': link.xpath('./text()').extract_first()
            })
        return documents

    def _parse_start(self, item, prev_item):
        start_datetime = self._parse_start_datetime(item, prev_item)
        return {
                'date': start_datetime.date(),
                'time': start_datetime.time(),
                'note': ''
        }

    def _parse_end(self, item, prev_item):
        start_datetime = self._parse_start_datetime(item, prev_item)
        return {
                'date': start_datetime.date(),
                'time': (start_datetime + timedelta(hours=3)).time(),
                'note': 'estimated 3 hours after start time'
        }

    def _parse_start_datetime(self, item, prev_item=None):
        """
        Parse start date and time.
        """
        date_el_text = item.css('td:first-child').extract_first()
        date_text = date_el_text[4:-5]
        date_str, time_str = [x.strip() for x in date_text.split('<br>')]
        # A.M. and AM formats are used inconsistently, remove periods
        time_str = time_str.replace('.', '')
        if re.match(r'\d{1,2}:\d{2} (AM|PM)', time_str):
            return datetime.strptime(date_str + time_str, '%m/%d/%Y%I:%M %p')
        # "Immediately after" specific meeting used frequently, return the
        # start time of the previous meeting
        elif prev_item is not None:
            return self._parse_start_datetime(prev_item)
              
    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
