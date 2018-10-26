# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re
from datetime import date, time

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiCityCollegeSpider(Spider):
    name = 'chi_city_college'
    agency_name = 'City Colleges of Chicago'
    allowed_domains = ['www.ccc.edu']

    start_urls = ['http://www.ccc.edu/events/Pages/default.aspx?dept=Office%20of%20the%20Board%20of%20Trustees']

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
        date, start_time, end_time = self._parse_date_and_times(response)
        data = {
            '_type': 'event',
            'name': self._parse_name(response),
            'event_description': self._parse_description(response),
            'classification': BOARD,
            'start': {
                'date': date,
                'time': start_time,
                'note': None,
            },
            'end': {
                'date': date,
                'time': end_time,
                'note': None,
            },
            'all_day': self._parse_all_day(),
            'status': self._parse_status(),
            'location': self._parse_location(response),
            'sources': self._parse_sources(response)
        }
        data['id'] = self._generate_id(data)
        return data

    def _parse_status(self):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

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
        text = response.css('#ctl00_PlaceHolderMain_FullDescription__ControlWrapper_RichHtmlField span::text').extract_first()
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

    def _parse_all_day(self):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        title = response.css('h1::text').extract_first()
        return 'Board of Trustees: {}'.format(title)

    def _parse_description(self, response):
        """
        Static description as given in Issue #275
        """
        return ("The Board of Trustees is the governing body of City Colleges "
                "of Chicago Community College District No. 508. City Colleges "
                "of Chicago currently operates seven accredited colleges "
                "located throughout Chicago.")

    def _time_from_parts(self, hour_string, minute_string, suffix):
        hour = int(hour_string)
        minute = int(minute_string)
        if suffix == "PM":
            hour += 12
        return time(hour, minute)

    def _parse_date_and_times(self, response):
        """
        Parse start date and time.
        """

        date_text = response.css('#formatDateA::text').extract_first()
        date_match = re.search(r"(\d+)\/(\d+)\/(\d+)", date_text)
        if date_match:
            date_value = date(month=int(date_match.group(1)), day=int(date_match.group(2)), year=int(date_match.group(3)))
        else:
            date_value = None

        time_text = response.css('.hours::text').extract_first()

        start_time_parts, end_time_parts = re.findall(r"(\d+):(\d{2})\s(AM|PM|noon)", time_text)

        return date_value, self._time_from_parts(*start_time_parts), self._time_from_parts(*end_time_parts),

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
