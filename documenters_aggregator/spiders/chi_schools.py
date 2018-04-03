# -*- coding: utf-8 -*-
from datetime import datetime

from documenters_aggregator.spider import Spider


class Chi_schoolsSpider(Spider):
    name = 'chi_schools'
    long_name = 'Chicago Public Schools Board of Education'
    allowed_domains = ['www.cpsboe.org']
    start_urls = ['http://www.cpsboe.org/meetings/planning-calendar']
    domain_url = 'http://www.cpsboe.org'

    def parse(self, response):
        for item in response.css('#content-primary tr')[1:]:
            start_time = self._parse_start_time(item)
            if start_time is not None:
                start_time = self._parse_start_time(item)
                data = {
                    '_type': 'event',
                    'name': 'Monthly Board Meeting',
                    'description': self._parse_description(item),
                    'classification': self._parse_classification(item),
                    'start_time': start_time,
                    'all_day': self._parse_all_day(item),
                    'timezone': 'America/Chicago',
                    'status': self._parse_status(item),
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(response)
                }
                data['id'] = self._generate_id(data, start_time)

                yield data

    def _remove_line_breaks(self, collection):
        return [x.strip() for x in collection if x.strip() != '']

    def _parse_description(self, item):
        """
        Currently every description is the same, but it's
        unsafe to assume that will always be the case so let's
        grab it programmatically anyways.
        """
        return ("The Chicago Board of Education is responsible for "
                "the governance, organizational and financial "
                "oversight of Chicago Public Schools (CPS), "
                "the third largest school district in the "
                "United States of America.")

    def _parse_classification(self, item):
        """
        @TODO Not implemented
        """
        return 'Not classified'

    def _parse_start_time(self, item):
        raw_strings = item.css('::text').extract()
        date_string = self._remove_line_breaks(raw_strings)[0]
        date_string = date_string.replace(' at', '')
        date_string = date_string.replace(',', "").replace(':', " ")
        try:
            date = datetime.strptime(date_string, '%B %d %Y %I %M %p')
            return self._naive_datetime_to_tz(date, 'America/Chicago')
        except:
            return None

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
        raw_text_list = item.css('::text').extract()
        text_list = self._remove_line_breaks(raw_text_list)[1:]
        text_list = [x for x in text_list if '(' not in x and ')' not in x]
        address = " ".join(text_list)
        return {
            'url': None,
            'address': address,
            'name': None,
            'coordinates': {
                'longitude': None,
                'latitude': None}
        }

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
