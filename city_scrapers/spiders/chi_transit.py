# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re

from datetime import datetime
from pytz import timezone
from city_scrapers.spider import Spider



class ChiTransitSpider(Spider):
    name = 'chi_transit'
    agency_id = 'Chicago Transit Authority'
    allowed_domains = ['www.transitchicago.com']
    base_url = 'http://www.transitchicago.com'
    timezone = 'America/Chicago'
    START_URL = 'https://www.transitchicago.com/board/notices-agendas-minutes/'
    start_urls = [START_URL]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        today = datetime.now().replace(tzinfo=timezone('America/Chicago'))
        response_items = response.css('.agendaminuteDataTbl tr:not(:first-child)')
        for idx, item in enumerate(response_items):
            # Including previous item for meetings where it's needed
            prev_item = response_items[idx - 1] if idx > 0 else None
            item_start = self._parse_start(item, prev_item)
            if item_start and today < item_start:
                item_name = self._parse_name(item)
                item_class = self._parse_classification(item)
                item_data = {
                    '_type': 'event',
                    'name': item_name,
                    'description': self._parse_description(item, item_class),
                    'classification': item_class,
                    'date':self._parse_start_date(item),
                    'time':self._parse_start_time(item),
                    'end_time': None,
                    'all_day': False,
                    'timezone': 'America/Chicago',
                    'status': self._parse_status(item),
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(response)
                }
                item_data['id'] = self._generate_id({'name': item_name})
                yield item_data

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
        status = 'tentative'
        name = item.css('td:nth-child(3)::text').extract_first()
        if re.search(r'cancelled', name, re.IGNORECASE):
            status = 'cancelled'
        return status

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        location_str = item.css('td:nth-child(4)::text').extract_first()
        # Always 537 W Lake, so handle that if provided (but allow for change)
        if re.search(r'567 (W.|W|West) Lake.*|board\s?room', location_str, re.IGNORECASE):
            return {
                'url': self.base_url,
                'name': 'Chicago Transit Authority 2nd Floor Boardroom',
                'address': '567 West Lake Street Chicago, IL',
                'coordinates': {
                    'latitude': '41.88528',
                    'longitude': '-87.64235',
                },
            }
        else:
            return {
                'url': None,
                'name': None,
                'address': location_str,
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
        date_str, time_str = [x.strip() for x in date_text.split('<br>')]
        # A.M. and AM formats are used inconsistently, remove periods
        time_str = time_str.replace('.', '')
        if re.match(r'\d{1,2}:\d{2} (AM|PM)', time_str):
            naive = datetime.strptime(date_str + time_str, '%m/%d/%Y%I:%M %p')
            return self._naive_datetime_to_tz(naive, 'America/Chicago')
        # "Immediately after" specific meeting used frequently, return the
        # start time of the previous meeting
        elif prev_item is not None:
            return self._parse_start(prev_item)
        
    def _parse_start_date(self, item):
        """
        Parse the date in the new format
        """
        date_el_text = item.css('td:first-child').extract_first()
        date_text = date_el_text[4:-5]
        date_text = date_text.replace(' ','')
        date_text = date_text.replace('\r\n', '')
        date_text = date_text.split('<br>')
        date_only = date_text[0]
        new_date_only = datetime.strptime(date_only, "%m/%d/%Y").strftime("date(%Y, %m, %d)")
        
    def _parse_start_time(self, item):
        """
        Parse the time in the new format
        """
        date_el_text = item.css('td:first-child').extract_first()
        date_text = date_el_text[4:-5]
        date_text = date_text.replace(' ','')
        date_text = date_text.replace('\r\n', '')
        date_text = date_text.split('<br>')
        time_only = date_text[1].replace('.','')
        time_only2 = self._conv_HH24(time_only)
        return time_only2
    
    def _conv_HH24(self, item):
        """
        Converts time with AM or PM into military time
        """
        ampm = item[-2]
        if ampm == "AM":
            rtrnTime = "time(" + item[:2] + ", " + item[3:-2] + ")"
            return rtrnTime
        else:
            hours = item[:2]
            new_hours = hours + 12
            rtrnTime = "time(" + new_hours + ", " + item[3:-2] + ")"
            return rtrnTime
        
    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
