# -*- coding: utf-8 -*-
import re

import dateutil.parser

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiDevelopmentFundSpider(Spider):
    name = 'chi_development_fund'
    agency_name = 'Chicago Department of Planning and Development'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = [
        'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_developmentfund.html'
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        columns = self.parse_meetings(response)
        for column in columns:
            meeting_date_xpath = """text()[normalize-space()]|
                                    p/text()[normalize-space()]|
                                    ul//text()[normalize-space()]"""
            meetings = column.xpath(meeting_date_xpath).extract()
            meetings = self.format_meetings(meetings)
            for meeting in meetings:
                start = self._parse_start(meeting)
                if start is None:
                    continue
                data = {
                    '_type': 'event',
                    'name': "Chicago Development Fund: {}".format(self._parse_name(meeting)),
                    'event_description': '',
                    'classification': COMMISSION,
                    'start': start,
                    'end': {
                        'date': start['date'],
                        'time': None,
                        'note': ''
                    },
                    'all_day': False,
                    'location': {
                        'neighborhood': '',
                        'name': 'City Hall',
                        'address': '121 N LaSalle St, Room 1000, Chicago, IL 60602'
                    },
                    'sources': [{
                        'url': response.url,
                        'note': ''
                    }],
                    'documents': self._parse_documents(column, meeting, response),
                }
                data['id'] = self._generate_id(data)
                data['status'] = self._generate_status(data)
                yield data

    @staticmethod
    def format_meetings(meetings):
        # translate and filter out non-printable spaces
        meetings = [meeting.replace('\xa0', ' ').strip() for meeting in meetings]
        meetings = list(filter(None, meetings))
        return meetings

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
                //td[preceding::strong[1]/text()[
                    contains(., "Meetings")
                    ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_name(meeting):
        if 'advisory' in meeting.lower():
            return 'Advisory Board'
        return 'Board of Directors'

    @staticmethod
    def _parse_start(meeting):
        # Not all dates on site a valid dates (e.g. Jan. 2011), so try to parse
        # and return none if not possible
        clean_str = re.sub(r'[\.,]', '', meeting)
        date_str = re.search(r'[a-zA-z]{1,10} \d{1,2} \d{4}', clean_str)
        if not date_str:
            return
        dt = dateutil.parser.parse(date_str.group())
        return {
            'date': dt.date(),
            'time': None,
            'note': 'See agenda for time',
        }

    def _parse_documents(self, item, meeting, response):
        # Find <a> tags where 1st, non-blank, preceding text = meeting (e.g. 'Jan 16')
        # site is pretty irregular and text is sometimes nested, so check siblings children
        # for meeting name if not found for sibling
        anchor_xpath = """
            //a[preceding-sibling::text()[normalize-space()][1][contains(., "{}")]]
        """.format(meeting)
        documents = item.xpath(anchor_xpath)
        if len(documents) >= 0:
            return [{
                'url': response.urljoin(document.xpath('@href').extract_first()),
                'note': document.xpath('text()').extract_first()
            } for document in documents]
        return []
