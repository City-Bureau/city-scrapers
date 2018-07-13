# -*- coding: utf-8 -*-
import re
from datetime import time

import dateutil.parser
import scrapy
from city_scrapers.spider import Spider


class Chi_development_fundSpider(Spider):
    name = 'chi_development_fund'
    agency_id = 'Department of Planning and Development'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_developmentfund.html']

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
            meeting_date_xpath = """text()[normalize-space()]|
                                    p/text()[normalize-space()]|
                                    ul//text()[normalize-space()]"""
            meetings = column.xpath(meeting_date_xpath).extract()
            meetings = self.format_meetings(meetings)
            for meeting in meetings:
                name, start = self._parse_start(meeting)
                data = {'_type': 'event',
                        'name': "Chicago Development Fund ({})".format(name),
                        'event_description': description,
                        'classification': 'Commission',
                        'start': start,
                        'all_day': False,
                        'location': {'neighborhood': '',
                                     'name': 'City Hall',
                                     'address': '121 N. LaSalle St., Room 1000'},
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
        desc_xpath = """
            //p[contains(text(), "The Chicago City Council established")]//text()
        """
        description = ' '.join(t.strip() for t in response.xpath(desc_xpath).extract())
        return description

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
                //td[preceding::strong[1]/text()[
                    contains(., "Meetings")
                    ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_start(meeting):
        # Not all dates on site a valid dates (e.g. Jan. 2011), so try to parse
        # and return none if not possible
        try:
            dt, other_text = dateutil.parser.parse(meeting, fuzzy_with_tokens=True)
            # based on Agenda mtg time seems to vary but time not stated mtg desc
            name = [s.strip() for s in other_text if s.strip()]
            return ' '.join(name), {'date': dt.date(), 'time': None, 'note': 'see agenda document for time'}
        except TypeError:
            name = ' '.join(meeting.split(' ')[:-3])
            return name, {'date': None, 'time': None, 'note': 'see agenda document for time'}

    def _parse_documents(self, item, meeting, response):
        # Find <a> tags where 1st, non-blank, preceding text = meeting (e.g. 'Jan 16')
        # site is pretty irregular and text is sometimes nested, so check siblings children
        # for meeting name if not found for sibling
        anchor_xpath = """
            //a[preceding-sibling::text()[normalize-space()][1][contains(., "{}")]]|
            //a[preceding-sibling::*//text()[normalize-space()][1][contains(., "{}")]]
        """.format(meeting, meeting)
        documents = item.xpath(anchor_xpath)
        if len(documents) >= 0:
            return [{'url': response.urljoin(document.xpath('@href').extract_first()),
                     'note': document.xpath('text()').extract_first()}
                    for document in documents]
        return [{}]
