# -*- coding: utf-8 -*-
from datetime import datetime

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiSchoolsSpider(Spider):
    name = 'chi_schools'
    agency_name = 'Chicago Public Schools Board of Education'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cpsboe.org']
    start_urls = ['http://www.cpsboe.org/meetings/planning-calendar']
    domain_url = 'http://www.cpsboe.org'

    def parse(self, response):
        event_description = self._parse_description(response)
        documents = self._parse_documents(response)
        for item in response.css('#content-primary tr')[1:]:
            start = self._parse_start_time(item)
            if start is not None:
                start = self._parse_start_time(item)
                data = {
                    '_type': 'event',
                    'name': 'Monthly Board Meeting',
                    'event_description': event_description,
                    'all_day': self._parse_all_day(item),
                    'classification': BOARD,
                    'start': start,
                    'documents': documents,
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(response),
                }
                data['id'] = self._generate_id(data)
                data['status'] = self._generate_status(data, event_description)
                data['end'] = {'date': data['start']['date'], 'time': None, 'note': ''}
                yield data

    def _parse_description(self, response):
        desc_xpath = '//table/following-sibling::ul//text()|//table/following-sibling::p//text()'
        desc_text = response.xpath(desc_xpath).extract()
        event_description = ' '.join(desc_text)
        return event_description

    def _remove_line_breaks(self, collection):
        return [x.strip() for x in collection if x.strip() != '']

    def _parse_start_time(self, item):
        raw_strings = item.css('::text').extract()
        date_string = self._remove_line_breaks(raw_strings)[0]
        date_string = date_string.replace(' at', '')
        date_string = date_string.replace(',', "").replace(':', " ")
        try:
            date = datetime.strptime(date_string, '%B %d %Y %I %M %p')
            return {
                'date': date.date(),
                'time': date.time(),
                'note': '',
            }
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
            'address': address,
            'name': None,
            'neighborhood': None,
        }

    def _parse_documents(self, response):
        # only extracting participation guidelines now
        relative_url = response.xpath('//a[contains(text(),"participation")]/@href').extract_first()
        url = response.urljoin(relative_url)
        return [
            {'url': url,
             'note': 'participation guidelines'
             }
        ]


    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
