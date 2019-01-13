# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

import scrapy

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiHousingAuthoritySpider(Spider):
    name = 'chi_housing_authority'
    agency_name = 'Chicago Housing Authority'
    timezone = 'America/Chicago'
    allowed_domains = ['www.thecha.org']
    start_urls = [
        'http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-information-and-meetings',  # noqa
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        if re.search(r'4859 S\.? Wabash', response.text) is None:
            raise ValueError('Meeting address has changed')

        req = scrapy.Request(
            'http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-meeting-notices',  # noqa
            callback=self._parse_next,
            dont_filter=True,
        )
        req.meta['upcoming'] = self._parse_upcoming(response)
        yield req

    def _parse_next(self, response):
        """Chains previous requests and yields a request to combine all results"""
        req = scrapy.Request(
            'http://www.thecha.org/doing-business/contracting-opportunities/view-all/Board%20Meeting',  # noqa
            callback=self._parse_combined_meetings,
            dont_filter=True,
        )
        req.meta['upcoming'] = self._parse_notice(response)
        yield req

    def _parse_upcoming(self, response):
        """Returns a list of dicts including the start date and status for upcoming meetings"""
        year_title = response.css('.text-area-full h2.text-align-center *::text').extract_first()
        upcoming_year = re.search(r'^\d{4}', year_title).group(0)
        date_list = []
        # Get list of month names to check in regular expression
        months = [datetime(int(upcoming_year), i, 1).strftime('%B') for i in range(1, 13)]
        for item in response.css('.text-area-full table.text-align-center td *::text'):
            item_text = item.extract()
            # See if text matches date regex, if so add to list
            date_match = re.search(r'({}) \d{{1,2}}'.format('|'.join(months)), item.extract())
            if date_match:
                date_str = '{} {}'.format(date_match.group(), upcoming_year)
                date_dict = {
                    'start': {
                        'date': datetime.strptime(date_str, '%B %d %Y').date()
                    },
                    'sources': [{
                        'url': response.url,
                        'note': ''
                    }],
                }
                date_dict['status'] = self._generate_status(date_dict, text=item_text)
                date_list.append(date_dict)
        return date_list

    def _parse_notice(self, response):
        """Returns a list of meetings with notice documents added to applicable dates"""
        notice_documents = self._parse_notice_documents(response)
        meetings_list = []
        for meeting in response.meta.get('upcoming', []):
            # Check if the meeting date is in any document title, if so, assign docs to that meeting
            meeting_date_str = '{dt:%B} {dt.day}'.format(dt=meeting['start']['date'])
            if any(meeting_date_str in doc['note'] for doc in notice_documents):
                meetings_list.append({
                    **meeting, 'documents': notice_documents,
                    'sources': [{
                        'url': response.url,
                        'note': ''
                    }]
                })
            else:
                meetings_list.append({**meeting, 'documents': []})
        return meetings_list

    def _parse_notice_documents(self, response):
        """Get document links from notice page, ignoring mailto and flyer links"""
        notice_documents = []
        for doc in response.css('article.full a[href]'):
            doc_text = doc.css('*::text').extract_first()
            if 'mailto' in doc.attrib['href'] or 'flyer' in doc_text.lower():
                continue
            notice_documents.append({
                'url': 'http://{}{}'.format(self.allowed_domains[0], doc.attrib['href']),
                'note': doc_text,
            })
        return notice_documents

    def _parse_combined_meetings(self, response):
        """Combines upcoming and past meetings and yields results ignoring duplicates"""
        meetings = self._parse_past_meetings(response)
        meeting_dates = [meeting['start']['date'] for meeting in meetings]

        for meeting in response.meta.get('upcoming', []):
            if meeting['start']['date'] not in meeting_dates:
                meetings.append(meeting)

        for meeting in meetings:
            item = {
                '_type': 'event',
                'name': 'Board of Commissioners',
                'event_description': '',
                'classification': BOARD,
                'start': {
                    'date': meeting['start']['date'],
                    'time': time(8, 30),
                    'note': 'Times may change based on notice',
                },
                'end': {
                    'date': meeting['start']['date'],
                    'time': time(13, 0),
                    'note': 'Times may change based on notice',
                },
                'all_day': False,
                'location': {
                    'address': '4859 S Wabash Chicago, IL 60615',
                    'name': 'Charles A. Hayes FIC',
                    'neighborhood': '',
                },
                'documents': meeting['documents'],
                'sources': meeting.get('sources', [{
                    'url': response.url,
                    'note': ''
                }]),
            }
            item['status'] = meeting.get('status', self._generate_status(item))
            item['id'] = self._generate_id(item)
            yield item

    def _parse_past_meetings(self, response):
        """Returns a list of start date and documents from meeting minutes page"""
        meetings = []
        for item in response.css('table.table-striped tbody tr'):
            dt_str = item.css('time::text').extract_first()
            meetings.append({
                'start': {
                    'date': datetime.strptime(dt_str, '%b %d, %Y').date()
                },
                'documents': self._parse_past_documents(item),
            })
        return meetings

    def _parse_past_documents(self, item):
        """Returns all documents for a past meeting"""
        doc_list = []
        for doc in item.css('a'):
            doc_list.append({
                'url': 'http://{}{}'.format(self.allowed_domains[0], doc.attrib['href']),
                'note': doc.css('*::text').extract_first(),
            })
        return doc_list
