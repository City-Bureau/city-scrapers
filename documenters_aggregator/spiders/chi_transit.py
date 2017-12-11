# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import scrapy

from datetime import datetime
from pytz import timezone
from slugify import slugify


class ChiTransitSpider(scrapy.Spider):
    name = 'chi_transit'
    long_name = 'Chicago Transit Authority'
    allowed_domains = ['www.transitchicago.com']
    base_url = 'http://www.transitchicago.com'
    start_urls = ['http://www.transitchicago.com/agendaminute/default.aspx?F_OrderBy=MeetingDate+DESC&All=y']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        today = datetime.now()
        response_items = response.css('.datatbl tr:not(:first-child)')
        for idx, item in enumerate(response_items):
            # Including previous item for meetings where it's needed
            prev_item = response_items[idx - 1] if idx > 0 else None
            item_start = self._parse_start(item, prev_item)
            if today < item_start:
                item_name = self._parse_name(item)
                item_class = self._parse_classification(item)
                yield {
                    '_type': 'event',
                    'id': self._parse_id(item_start, item_name),
                    'name': item_name,
                    'description': self._parse_description(item, item_class),
                    'classification': item_class,
                    'start_time': self._format_datetime(item_start),
                    'end_time': None,
                    'all_day': False,
                    'timezone': 'America/Chicago',
                    'status': self._parse_status(item),
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(response)
                }

    def _parse_id(self, start_time, name):
        """
        We use the start time to generate an ID since there is no publically
        exposed meeting ID.
        """
        return slugify(start_time.strftime('%Y-%m-%d-') + name)

    def _parse_classification(self, item):
        """
        Parse or generate classification, CTA uses one of three consistently
        """
        return item.css('td:nth-child(2)::text').extract_first()

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        location_str = item.css('td:nth-child(4)::text').extract_first()
        # Always 537 W Lake, so handle that if provided (but allow for change)
        if re.match(r'567 (W.|W|West) Lake.*', location_str):
            return {
                'url': self.base_url,
                'name': '567 West Lake Street, 2nd Floor, Boardroom, Chicago, IL',
                'coordinates': {
                    'latitude': 41.88528,
                    'longitude': -87.64235,
                },
            }
        else:
            return {
                'url': None,
                'name': location_str,
                'coordinates': {
                    'latitude': None,
                    'longitude': None
                },
            }

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item.css('td:nth-child(3)::text').extract_first()

    def _parse_description(self, item, classification):
        """
        Combine classification with any links present.
        """
        description = classification
        link_items = item.css('td:last-child a')
        if len(link_items):
            description += ' - '
        for link in link_items:
            description += ' {}: {}{}'.format(
                link.xpath('./text()').extract_first(),
                self.base_url,
                link.xpath('./@href').extract_first()
            )

        return description

    def _parse_start(self, item, prev_item=None):
        """
        Parse start date and time.
        """
        date_el_text = item.css('td:first-child').extract_first()
        date_text = date_el_text[4:-5]
        date_str, time_str = date_text.split('<br>')
        # A.M. and AM formats are used inconsistently, remove periods
        time_str = time_str.replace('.', '')
        if re.match(r'\d{1,2}:\d{2} (AM|PM)', time_str):
            return datetime.strptime(date_str + time_str, '%m/%d/%Y%I:%M %p')
        # "Immediately after" specific meeting used frequently, return the
        # start time of the previous meeting
        elif prev_item is not None:
            return self._parse_start(prev_item)

    def _format_datetime(self, time):
        """
        Format datetime as timezone-aware,
        ISO-formatted string.
        """
        tz = timezone('America/Chicago')
        return tz.localize(time).isoformat()

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
