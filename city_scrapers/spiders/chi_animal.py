# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import datetime
from dateutil.parser import parse as dateparse
from city_scrapers.spider import Spider


class Chi_animalSpider(Spider):
    name = 'chi_animal'
    agency_id = 'Animal Care and Control Commission'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.page-full-description').css("ul").css("li"):
            # Pull the string
            try:
                text = item.xpath("text()").extract()[0]
            except IndexError:
                continue

            # Strip it
            text = text.strip()

            # Pass if there's nothing left
            if not text:
                continue

            # Parse the item
            data = {
                '_type': 'event',
                'name': self._parse_name(text),
                'event_description': self._parse_description(text),
                'classification': self._parse_classification(text),
                'start': self._parse_start(text),
                'all_day': self._parse_all_day(text),
                'location': self._parse_location(text),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._parse_status(data)
            data['end'] = self._generate_end(data['start'])

            yield data

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Commission'

    def _parse_status(self, data):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        start_date = data['start']['date']
        today = datetime.date.today()
        if start_date < today:
            return 'passed'

        if start_date <= (today + datetime.timedelta(days=7)):
            return 'confirmed'

        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        return {
            'name': 'David R. Lee Animal Care Center',
            'address': '2741 S. Western Ave, Chicago, IL 60608',
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return 'Animal Care and Control Commission meeting'

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        naive_datetime = self._naive_datetime_to_tz(dateparse(item))
        return {
            'date': naive_datetime.date(),
            'time': naive_datetime.time(),
        }

    def _generate_end(self, start):
        """
        Estimate end date and time.
        """
        start_dt = datetime.datetime.combine(start['date'], start['time'])
        end_dt = start_dt + datetime.timedelta(hours=3)
        return {
            'date': end_dt.date(),
            'time': end_dt.time(),
            'note': 'estimated 3 hours after the start time',
        }

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
