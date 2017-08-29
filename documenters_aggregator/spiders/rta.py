# -*- coding: utf-8 -*-
import scrapy

import re
from datetime import datetime
from pytz import timezone


# The RTA's Board and other meetings are are displayed on their
# website via an iframe from a different domain.
class RtaSpider(scrapy.Spider):
    name = 'rta'
    allowed_domains = ['www.rtachicago.org', 'rtachicago.granicus.com']
    start_urls = ['http://www.rtachicago.org/about-us/board-meetings']
    domain_root = 'http://www.rtachicago.org'

    def parse_iframe(self, response):
        description = response.request.meta['description']
        for item in response.css('#upcoming .row'):
            start_time = self._parse_start(item)
            name = self._parse_name(item)
            yield {
                '_type': 'event',
                'id': self._generate_id(start_time, name),
                'name': name,
                'description': description,
                'classification': self._parse_classification(item),
                'start_time': start_time,
                'end_time': None,
                'all_day': False,
                'status': self._parse_status(item),
                'location': self._parse_location(item),
            }

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

    def _generate_id(self, start_time, name):
        """
        We use the start time to generate an ID since there is no publically
        exposed meeting ID.
        """

        date = start_time.split('T')[0]
        dashified = re.sub(r'[^a-z]+', '-', name.lower())
        return '{0}-{1}'.format(date, dashified)

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
            'coordinates': None,
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
        tz = timezone('America/Chicago')
        naive_dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 8, 30)
        dt = tz.localize(naive_dt)
        return dt.isoformat()
