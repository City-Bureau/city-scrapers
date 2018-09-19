# -*- coding: utf-8 -*-
import re
from datetime import time

import dateutil.parser

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiCommunityDevelopmentSpider(Spider):
    name = 'chi_community_development'
    agency_name = 'Chicago Department of Planning and Development'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/dcd/supp_info/community_developmentcommission.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        description = self.parse_description(response)
        columns = self.parse_meetings(response)
        for column in columns:
            year = column.xpath('preceding::h3[1]/text()').re_first(r'(\d{4})(.*)')
            meeting_date_xpath = 'text()[normalize-space()]|p/text()[normalize-space()]'
            meetings = column.xpath(meeting_date_xpath).extract()
            meetings = self.format_meetings(meetings)
            for meeting in meetings:
                data = {'_type': 'event',
                        'name': 'Community Development Commission',
                        'event_description': description,
                        'classification': 'Commission',
                        'start': self._parse_start(meeting, year), 'all_day': False,
                        'location': {'neighborhood': '',
                                     'name': 'City Hall',
                                     'address': '121 N. LaSalle St., Room 201A'},
                        'sources': [{'url': response.url, 'note': ''}],
                        'documents': self._parse_documents(column, meeting, response)}
                data['end'] = {'date': data['start']['date'], 'time': None, 'note': ''}
                data['id'] = self._generate_id(data)
                data['status'] = self._generate_status(data, '')
                yield data

    @staticmethod
    def format_meetings(meetings):
        # translate and filter out non-printable spaces
        meetings = [meeting.replace('\xa0', ' ').strip() for meeting in meetings]
        meetings = list(filter(None, meetings))
        return meetings

    @staticmethod
    def parse_description(response):
        desc_xpath = '//p[contains(text(), "The Community Development Commission")]//text()'
        description = ' '.join(t.strip() for t in response.xpath(desc_xpath).extract())
        return description

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
                //td[preceding::h3[1]/text()[
                    contains(., "Meeting Schedule")
                    ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_start(meeting, year):
        m = re.search(r'(?P<month>\w+)\.?\s(?P<day>\d+).*', meeting.strip())
        dt = dateutil.parser.parse(m.group('month') + ' ' + m.group('day') + ' ' + year)
        # time based on examining meeting minutes
        return {'date': dt.date(), 'time': time(1, 00), 'note': ''}

    def _parse_documents(self, item, meeting, response):
        # Find <a> tags where 1st, non-blank, preceding text = meeting (e.g. 'Jan 16')
        anchor_xpath = """
            a[preceding-sibling::text()[normalize-space()][1][contains(., "{}")]]
        """.format(meeting)
        documents = item.xpath(anchor_xpath)
        if len(documents) >= 0:
            return [{'url': response.urljoin(document.xpath('@href').extract_first()),
                     'note': document.xpath('text()').extract_first()}
                    for document in documents]
        return [{}]
