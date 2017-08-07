# -*- coding: utf-8 -*-
import scrapy

import re
from datetime import datetime
from pytz import timezone

# The RTA's Board and other meetings are are displayed on their
# website via an iframe from a different domain.
class RtaSpider(scrapy.Spider):
    name = 'rta'
    allowed_domains = ['http://www.rtachicago.org', 'http://rtachicago.granicus.com']
    start_urls = ['http://www.rtachicago.org/about-us/board-meetings']
    domain_root = 'http://www.rtachicago.org'

    def parse_iframe(self, response):
        description = response.request.meta['description']
        for item in response.css('#upcoming .row'):
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': description,
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
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

        request = scrapy.Request(url, callback = self.parse_iframe)
        request.meta['description'] = description

        yield request

    def _parse_id(self, item):
        """
        There is no publicly exposed ID.
        """
        return None

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
        @TODO better location
        """
        return {
            'url': '',
            'name': 'See description',
            'coordinates': None,
        }

    def _parse_all_day(self, item):
        """
        It appears all events have a start and end time on the IPDH website,
        so this `all_day` is always false.
        """
        return False

    def _parse_name(self, item):
        """
        Get event name
        """
        title = item.css('.committee::text').extract_first()
        return title.split(' on ')[0]

    def _parse_description(self, item):
        """
        Get event description from `div.event_description`'
        """
        lines = item.css('div.event_description p::text').extract()
        lines = [line.strip() for line in lines]
        return '\n'.join(lines)

    def _parse_start(self, item):
        """
        Combine start time with year, month, and day.
        """
        title = item.css('.committee::text').extract_first()
        m = re.search('(\d{4})-(\d{1,2})-(\d{1,2})', title)
        tz = timezone('America/Chicago')
        naive_dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 8, 30)
        dt = tz.localize(naive_dt, is_dst=False)
        return dt.isoformat()

    def _parse_end(self, item):
        """
        End times are not posted.
        """
        return None
