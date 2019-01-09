# -*- coding: utf-8 -*-
import datetime
import re

from lxml import etree

from city_scrapers.constants import ADVISORY_COMMITTEE
from city_scrapers.spider import Spider


class ArchiveParserMixin:
    def _parse_archive_documents(self, response):
        '''
        Documents live in a series of <p> elements, structured like:

            Year
            Month Day, Year Agenda – Meeting Minutes – Presentations

        There is a line for each scheduled meeting. Agenda, Meeting Minutes,
        and Presentations are links, where there is a document available.
        '''
        for p in response.xpath('//p'):
            if self._contains_year(p):
                blob = p.extract().splitlines()
                yield from self._parse_document_blob(blob)

    def _contains_year(self, element):
        return element.xpath('text()') and \
            re.match(r'\d{4}', element.xpath('text()')[0].extract())

    def _tree_from_fragment(self, fragment):
        '''
        Coerce HTML fragments from into parse-able blobs.
        '''
        return etree.HTML(fragment).xpath('//p')[0]

    def _parse_document_blob(self, blob):
        for line in blob[1:]:  # Omit header
            element = self._tree_from_fragment(line)

            date = ' '.join(element.text.split(' ')[:3])

            documents = []

            for doc in element.iterchildren('a'):
                documents.append({
                    'url': doc.attrib['href'],
                    'note': doc.text.lower().strip(),
                })

            yield date, documents


class ChiMayorsBicycleAdvisoryCouncilSpider(Spider, ArchiveParserMixin):
    name = 'chi_mayors_bicycle_advisory_council'
    agency_name = "Mayor's Bicycle Advisory Council"
    timezone = 'America/Chicago'
    allowed_domains = ['chicagocompletestreets.org']

    BASE_URL = 'http://chicagocompletestreets.org/getinvolved/' + \
        'mayors-advisory-councils/'

    start_urls = [BASE_URL + 'mbac-meeting-archives/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for date, documents in self._parse_archive_documents(response):

            data = {
                '_type': 'event',
                'name': self._parse_name(),
                'event_description': self._parse_description(),
                'classification': self._parse_classification(),
                'start': self._parse_start(date),
                'end': self._parse_end(date),
                'all_day': self._parse_all_day(),
                'location': self._parse_location(),
                'documents': documents,
                'sources': self._parse_sources(),
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_name(self):
        """
        Parse or generate event name.
        """
        return "Mayor's Bicycle Advisory Council"

    def _parse_description(self):
        """
        Parse or generate event description.
        """
        return 'MBAC focuses on a wide range of bicycle issues: safety, ' + \
            'education, enforcement, and infrastructure investment. The Council ' + \
            'will help identify issues, discuss ideas and set priorities for ' + \
            'bicycle planning in Chicago.'

    def _parse_classification(self):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return ADVISORY_COMMITTEE

    def _parse_year(self, header):
        '''
        Dates are not listed with a year. Grab it from the date listing header,
        e.g., "The 2018 MBAC meeting dates:"
        '''
        header_text, = header.xpath('strong/span/text()').extract()

        return re.search(r'\d{4}', header_text).group(0)

    def _parse_start(self, item):
        """
        Parse start date and time like "Wednesday, March 7, 2017."
        """
        date = datetime.datetime.strptime(item, '%B %d, %Y').date()

        return {
            'date': date,
            'time': datetime.time(15, 0),
            'note': 'Start at 3 p.m. unless otherwise noted'
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        date = datetime.datetime.strptime(item, '%B %d, %Y').date()

        return {'date': date, 'time': None, 'note': ''}

    def _parse_all_day(self):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': '121 N LaSalle Dr, Chicago, IL',
            'name': 'City Hall, Room 1103',
            'neighborhood': 'Loop',
        }

    def _parse_sources(self):
        """
        Parse or generate sources.
        """
        listing_url = {'url': self.BASE_URL, 'note': ''}
        archive_url = {'url': self.start_urls[0], 'note': 'documents'}
        return [listing_url, archive_url]
