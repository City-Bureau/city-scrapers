# -*- coding: utf-8 -*-
import scrapy

import re
from datetime import datetime

from documenters_aggregator.spider import Spider


# The RTA's Board and other meetings are are displayed on their
# website via an iframe from a different domain.
class RegionaltransitSpider(Spider):
    name = 'regionaltransit'
    long_name = 'Regional Transportation Authority'
    allowed_domains = ['www.rtachicago.org', 'rtachicago.granicus.com']
    start_urls = ['http://www.rtachicago.org/about-us/board-meetings']
    domain_root = 'http://www.rtachicago.org'

    def parse_iframe(self, response):
        description = response.request.meta['description']
        for item in response.css('#upcoming .row'):
            start_time = self._parse_start(item)
            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'description': description,
                'classification': self._parse_classification(item),
                'start_time': start_time,
                'end_time': None,
                'all_day': False,
                'timezone': 'America/Chicago',
                'status': self._parse_status(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data, start_time)
            yield data

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.
        """

        description = response.css('.show_item_intro_text p::text').extract_first()

        url = response.css('iframe::attr(src)').extract_first()

        request = scrapy.Request(url, callback=self.parse_iframe)
        request.meta['description'] = description

        # Disable built-in RobotsTxt middleware for this request.
        request.meta['dont_obey_robotstxt'] = True

        yield request

    def _parse_classification(self, item):
        """
        @TODO Not implemented
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        @TODO determine correct status
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        The location is hard coded based on the value shown on the meetings page. It
        is not expected to change often, so this is probably OK.
        """
        return {
            'url': 'http://www.rtachicago.org/index.php/about-us/contact-us.html',
            'name': 'RTA Administrative Offices',
            'coordinates': {'longitude': '', 'latitude': ''},
            'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604'
        }

    def _parse_name(self, item):
        """
        Get event name
        """
        title = item.css('.committee::text').extract_first()
        return title.split(' on ')[0]

    def _parse_start(self, item):
        """
        Retrieve the event date, always using 8:30am as the time.
        """
        title = item.css('.committee::text').extract_first()
        m = re.search('(\d{4})-(\d{1,2})-(\d{1,2})', title)
        naive_dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 8, 30)
        return self._naive_datetime_to_tz(naive_dt, 'America/Chicago')

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
