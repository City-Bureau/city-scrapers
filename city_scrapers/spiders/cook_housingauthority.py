# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from dateutil.parser import parse as dateparse
from datetime import datetime
from pytz import timezone

from city_scrapers.spider import Spider


class Cook_housingAuthoritySpider(Spider):
    name = 'cook_housingauthority'
    long_name = 'Housing Authority of Cook County'    
    allowed_domains = ['http://thehacc.org/']
    start_urls = ['http://thehacc.org/events/feed/']
    event_timezone = 'America/Chicago'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        #events = response.css('item')

        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

        #for event in events:
        #    yield self._parse_event(event)



    def _parse_event(self, response):
        """
        Parse the event page.
        """
        start_time, end_time = self._parse_date_time(response)
        data = {
            '_type': 'event',
            'name': response.css('h3.entry-title::text').extract_first(),
            'description': self._parse_description(response),
            'classification': self._parse_classification(),
            'start_time': start_time,
            'end_time': end_time,
            'all_day': self._parse_all_day(response),
            'timezone': self.event_timezone,
            'status': self._parse_status(response),
            'location': self._parse_location(response),
            'sources': [{'url': response.url, 'note': ''}]
        }
        data['id'] = self._generate_id(data, start_time)
        return data

    def _get_event_urls(self, response):
        return response.css('item link::text').extract()

    def _parse_date_time(self, response):
        '''
        '''
        date = response.css('div.dtstart::attr(title)').extract_first()
        time_range = response.css('div.dtstart::text').extract_first().strip()
        time_list = time_range.split(' - ')

        start_time = dateparse(' '.join([date, time_list[0]]))
        end_time = dateparse(' '.join([date, time_list[1]]))

        return self._naive_datetime_to_tz(start_time), self._naive_datetime_to_tz(end_time)


    def _parse_description(self, response):
        desc = response.css('div.description::text').extract_first().strip()

        if desc is None:
            return ""
        else:
            return desc

            
    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        name = response.css('dd.tribe-venue::text').extract_first().strip()
        street_address = response.css('span.tribe-street-address::text').extract_first().strip()
        city = response.css('span.tribe-locality::text').extract_first().strip()
        state = response.css('abbr.tribe-region::text').extract_first().strip()
        zipcode = response.css('span.tribe-postal-code::text').extract_first().strip()

        address = [street_address, city, state, zipcode]

        address = ' '.join([x for x in address])
        
        return {
            'url': None,
            'address': address,
            'name': name,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_classification(self):

        return 'Not classified'

    def _parse_all_day(self, response):
        
        return False

    def _parse_status(self, response):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'