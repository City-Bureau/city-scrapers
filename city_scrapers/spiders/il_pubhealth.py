# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin

import scrapy
import usaddress
from dateutil.parser import parse as dateparse

from city_scrapers.spider import Spider


class Il_pubhealthSpider(Spider):
    name = 'il_pubhealth'
    agency_id = 'Illinois Department of Public Health'
    timezone = 'America/Chicago'

    long_name = 'Illinois Department of Public Health'
    allowed_domains = ['www.dph.illinois.gov']
    start_urls = ['http://www.dph.illinois.gov/events']
    domain_root = 'http://www.dph.illinois.gov'
    chicago_matcher_regex = re.compile('Chicago')

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.
        """
        for item in response.css('.eventspage'):
            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'event_description': self._parse_description(item),
                'classification': 'Not classified',
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'documents': self._parse_documents(item, response.url),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')
            yield data

        yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page.
        """
        next_url = response.css('.pager-next a::attr(href)').extract_first()
        next_url = '{0}{1}'.format(self.domain_root, next_url)
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Getting the internal ID is ugly. We need to grab a string like
        "addtocal_node_16206" and grab only the end.
        """
        raw_id_string = item.css('div.addtocal::attr(id)').extract_first()
        return raw_id_string.split('_')[-1]

    def _parse_location(self, item):
        """
        @TODO better location
        """
        lines = item.css('div.event_description p::text').extract()
        lines = [line.strip() for line in lines]

        address = self._find_high_confidence_address(lines)
        if address is None:
            address = self._find_medium_confidence_address(lines)
        if address is None:
            address = self._find_low_confidence_address(lines)
        if address is None:
            address = 'multiple locations not in Chicago, see description'

        return {
            'name': '',
            'address': address,
            'neighborhood': '',
        }

    def _find_high_confidence_address(self, lines):
        for line in lines:
            try:
                tagged_address, address_type = usaddress.tag(line)
                if address_type  == "Street Address" and tagged_address.get("PlaceName") == "Chicago":
                    return line
            except usaddress.RepeatedLabelError:
                pass
        else:
            return None

    def _find_medium_confidence_address(self, lines):
        for line in lines:
            parsed_address = usaddress.parse(line)
            for address_component in parsed_address:
                if address_component[1]  == "PlaceName" and address_component[0] == "Chicago":
                    return line
        else:
            return None

    def _find_low_confidence_address(self, lines):
        for line in lines:
            if self.chicago_matcher_regex.search(line):
                return line
        else:
            return None

    def _parse_all_day(self, item):
        """
        It appears all events have a start and end time on the IPDH website,
        so this `all_day` is always false.
        """
        return False

    def _parse_name(self, item):
        """
        Get event name from `div.eventtitle`'
        """
        return item.css('div.eventtitle::text').extract_first()

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
        start = item.css('div span.date-display-start::attr(content)').extract_first()
        if start == '':
            start = item.css('div span.date-display-single::attr(content)').extract_first()
        dt = dateparse(start)
        return {'date': dt.date(), 'time': dt.time(), 'note': ''}

    def _parse_end(self, item):
        """
        Combine end time with year, month, and day.
        """
        match = item.css('div span.date-display-end::attr(content)').extract_first()
        if match:
            dt = dateparse(match)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        return {'date': None, 'time': None, 'note': ''}

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]

    def _parse_documents(self, item, base_url):
        documents = []
        agenda = item.xpath('.//a[contains(., "Agenda")]/@href').extract_first()
        if agenda:
            documents.append({'url': urljoin(base_url, agenda), 'note': 'agenda'})
        return documents
