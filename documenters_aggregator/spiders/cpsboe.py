# -*- coding: utf-8 -*-
import scrapy

from datetime import datetime
from pytz import timezone


class CpsboeSpider(scrapy.Spider):
    name = 'cpsboe'
    allowed_domains = ['www.cpsboe.org']
    start_urls = ['http://www.cpsboe.org/meetings/planning-calendar']
    domain_url = 'http://www.cpsboe.org'

    def parse(self, response):
        for item in response.css('#content-primary tr')[1:]:
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': 'Chicago Board of Education Monthly Meeting',
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start_time(item),
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item)

            }

    def _parse_id(self, item):
        """
        Generate an ID by converting the date and time to an integer.
        i.e. 'July 27, 2016 at 10:30am' becomes '201707261030'
        """
        text_list = self._remove_line_breaks(item.css('::text').extract())
        split_date_string = text_list[0].split()
        split_date_string[0] = split_date_string[0][:3]
        split_date_string[1] = split_date_string[1][:-1]
        split_date_string[3] = ''
        date_string = " ".join(split_date_string)
        date_string = date_string.replace(':', ' ')
        date = datetime.strptime(date_string, '%b %d %Y %I %M %p')
        return str(
            100000000 * date.year +
            1000000 * date.month +
            10000 * date.day +
            100 * date.hour +
            date.minute
            )

    def _remove_line_breaks(self, collection):
        while '\n' in collection:
            collection.remove("\n")
        return collection

    def _parse_description(self, item):
        """
        Currently every description is the same, but it's
        unsafe to assume that will always be the case so let's
        grab it programmatically anyways.
        """
        raw_text_list = item.css('td')[1].css('::text').extract()
        text_list = self._remove_line_breaks(raw_text_list)
        description = "\n".join(text_list)
        return description

    def _parse_classification(self, item):
        """
        @TODO Not implemented
        """
        return 'Not classified'

    def _parse_start_time(self, item):
        raw_strings = item.css('td')[0].css('::text').extract()
        date_string = self._remove_line_breaks(raw_strings)[0]
        date_string = date_string.replace(' at', '')
        date_string = date_string.replace(',', "").replace(':', " ")
        date = datetime.strptime(date_string, '%B %d %Y %I %M %p')
        tz = timezone('America/Chicago')
        return tz.localize(date).isoformat()

    def _parse_all_day(self, item):
        """
        Looking around at youtube videos of past meetings it looks like the
        typical duration is 2-3 hours.
        """
        return False

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
