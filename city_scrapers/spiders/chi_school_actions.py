# -*- coding: utf-8 -*-
import itertools
from datetime import datetime

from city_scrapers.constants import FORUM
from city_scrapers.spider import Spider


class ChiSchoolActionsSpider(Spider):
    name = 'chi_school_actions'
    agency_name = 'Chicago Public Schools School Actions'
    timezone = 'America/Chicago'
    allowed_domains = ['schoolinfo.cps.edu']
    start_urls = ['http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for school in response.css('#wrapper > table > tr'):
            school_name = school.css('td:first-child span::text').extract_first()
            school_action = school.css('td:nth-child(2) p > span::text').extract_first().strip()
            school_docs = self._parse_documentation(school)

            for meeting_section in school.css('#main-body > table > tr > td > table > tr'):
                meeting_type = self._parse_meeting_type(meeting_section, school_action)
                for meeting in meeting_section.css('td > table'):
                    start = self._parse_start(meeting)
                    end = self._parse_end(meeting)
                    item_name = self._parse_name(school_name, meeting_type)
                    item = {
                        '_type': 'event',
                        'name': item_name,
                        'all_day': False,
                        'event_description': self._parse_description(school_name, meeting_type),
                        'classification': FORUM,
                        'start': start,
                        'end': end,
                        'documents': school_docs,
                        'location': self._parse_location(meeting),
                        'sources': self._parse_sources(),
                    }
                    item['id'] = self._generate_id(item)
                    item['status'] = self._generate_status(item, '')
                    yield item

    def _parse_name(self, school_name, meeting_type):
        """
        Parse or generate event name.
        """
        return '{} {}'.format(school_name, meeting_type)

    @staticmethod
    def _parse_description(school_name, meeting_type):
        """
        Parse or generate event description.
        """
        return '{} {}'.format(school_name, meeting_type)

    @staticmethod
    def _parse_meeting_type(item, school_action):
        return '{}: {}'.format(
            item.css('td > p.sub-title:first-of-type::text').extract_first(),
            school_action
        )

    @staticmethod
    def _parse_date_str(item):
        """
        Parse date, return as %Y-%b-%d string
        """
        year = item.css('.year::text').extract_first()
        month = item.css('.month::text').extract_first()
        day = item.css('.day::text').extract_first()
        return '{}-{}-{}'.format(year, month, day)

    @staticmethod
    def _parse_datetime_str(date_str, time_str):
        """
        Parse datetime string from date and time strings
        """
        time_str = time_str.strip().replace('.', '')[:]
        # Enforce max length, select format string
        if ':' in time_str:
            time_str = time_str[:7]
            time_format_str = '%I:%M %p'
        else:
            time_str = time_str[:4]
            time_format_str = '%I %p'
        return datetime.strptime(date_str + time_str, '%Y-%b-%d' + time_format_str)

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date_str = self._parse_date_str(item)
        time = item.css('.time::text').extract_first()
        dt = self._parse_datetime_str(date_str, time.split('-')[0])
        return {
            'date': dt.date(),
            'time': dt.time(),
            'note': ''
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        date_str = self._parse_date_str(item)
        time = item.css('.time::text').extract_first()
        split_time = time.split('-')
        if len(split_time) > 1:
            dt = self._parse_datetime_str(date_str, split_time[1])
            return {
                'date': dt.date(),
                'time': dt.time(),
                'note': ''
            }
        else:
            return self._parse_start(item)

    @staticmethod
    def _parse_location(item):
        """
        Parses location, adding Chicago, IL to the end of the address
        since it isn't included but can be safely assumed.
        """
        address = item.css('.addr2::text').extract_first()
        return {
            'name': item.css('.addr::text').extract_first(),
            'address': address + ' Chicago, IL',
            'neighborhood': '',
        }

    def _parse_sources(self):
        """
        Parse or generate sources.
        """
        return [{'url': self.start_urls[0], 'note': ''}]

    @staticmethod
    def _parse_documentation(school):
        """
        Parsing the documentation and meeting note URLs
        """
        doc_link_list = []
        doc_link_items = school.css('ul.bullets:first-of-type li')
        note_link_items = school.css('ul.bullets:nth-of-type(2) li')

        for item in itertools.chain(doc_link_items, note_link_items):
            doc_link_list.append(
                {
                    'note': item.css('a::text').extract_first(),
                    'url': 'http://schoolinfo.cps.edu/SchoolActions/' + item.css('a::attr(href)').extract_first(),
                }
            )
        return doc_link_list
