# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
from dateutil.parser import parse as dateparse
from documenters_aggregator.spider import Spider


class Chi_animalSpider(Spider):
    name = 'chi_animal'
    long_name = 'Animal Care and Control Commission'
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
                'description': self._parse_description(text),
                'classification': self._parse_classification(text),
                'start_time': self._parse_start(text),
                'end_time': self._parse_end(text),
                'all_day': self._parse_all_day(text),
                'timezone': 'America/Chicago',
                'status': self._parse_status(text),
                'location': self._parse_location(text),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data, data['start_time'])

            yield data

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

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
        return {
            'url': None,
            'name': 'David R. Lee Animal Care Center',
            'address': '2741 S. Western Ave, Chicago, IL 60608',
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
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
        return 'Commission meeting'

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        item = '-'.join(item.split('-')[:2]).strip()
        naive_date = dateparse(item)
        return self._naive_datetime_to_tz(naive_date)

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return None

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
