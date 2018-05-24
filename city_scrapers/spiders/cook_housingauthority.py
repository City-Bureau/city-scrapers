# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

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
        # events = response.css('item')

        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

        # for event in events:
        #    yield self._parse_event(event)

    def _parse_event(self, response):
        """
        Parse the event page.
        """
        raw_meeting_details = response.xpath(
            "//header/h3[@class='entry-title']/following-sibling::p/text()").extract_first()
        details = self._parse_raw_details_string(raw_meeting_details)
        start_time, end_time = self._parse_date_time(details)
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
            'location': details['location'],
            'sources': [{'url': response.url, 'note': ''}]
        }
        data['id'] = self._generate_id(data, start_time)
        return data

    def _get_event_urls(self, response):
        return response.css('item link::text').extract()

    def _parse_date_time(self, details):
        '''
        '''
        start_time = dateparse('{date} {time}'.format(date=details['date'], time=details['start_time']))
        end_time = dateparse('{date} {time}'.format(date=details['date'], time=details['end_time']))
        return self._naive_datetime_to_tz(start_time), self._naive_datetime_to_tz(end_time)

    @staticmethod
    def _parse_raw_details_string(raw_meeting_details):
        """
        Parse meeting details from raw string
            June 12, 2018, 1:00 pm - 2:30 pm 15306 S. Robey Ave.
        """
        matches = re.search('(.*(?: am | pm ))(.*)', raw_meeting_details)
        date = re.search('(.*,.*), (.*)', matches.group(1))
        address = matches.group(2)
        time_list = date.group(2).split(' - ')
        start_time = time_list[0].strip()
        end_time = time_list[1].strip()
        date = date.group(1)
        location = {
            'url': None,
            'address': address,
            'name': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }
        return {
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'location': location
        }

    def _parse_description(self, response):
        desc = response.css('div.description::text').extract_first().strip()

        if desc is None:
            return ""
        else:
            return desc

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
