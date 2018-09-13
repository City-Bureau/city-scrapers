# -*- coding: utf-8 -*-
import re
from collections import defaultdict

from dateutil.parser import parse

from city_scrapers.constants import ADVISORY_COMMITTEE, BOARD, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class DetBrownfieldRedevelopmentAuthoritySpider(Spider):
    name = 'det_brownfield_redevelopment_authority'
    agency_name = 'Detroit Brownfield Redevelopment Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/dbra/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        yield from self._prev_meetings(response)
        yield from self._next_meeting(response)

    def _next_meeting(self, response):
        # the two meetings seem to always be held back-to-back,
        # so generate two meetings for each entry
        next_meeting_xpath = '//p[contains(., "The next regularly scheduled DBRA meeting ")]//text()'
        next_meeting_text = ' '.join(response.xpath(next_meeting_xpath).extract())
        for i, meeting in enumerate(('Board of Directors', 'Community Advisory Committee')):
            data = self._set_meeting_defaults(response, meeting)
            data['start'] = self._parse_start(next_meeting_text, i)
            data['documents'] = []
            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)
            yield data

    def _prev_meetings(self, response):
        prev_meetings_xpath = '//a[contains(., "Agendas, and Minutes")]'
        prev_meetings = response.xpath(prev_meetings_xpath)
        for a in prev_meetings:
            yield response.follow(a, callback=self._parse_prev_meetings)

    def _parse_start(self, date_time_text, meeting_number):
        time_match = self._parse_time(date_time_text)
        date_match = self._parse_date(date_time_text)
        try:
            dt = parse(date_match.group(1) + ' ' + time_match[meeting_number][0], fuzzy=True)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': ''}

    def _parse_prev_meetings(self, response):
        # there are only documents for prev meetings,
        # so use these to create prev meetings
        prev_meeting_docs = self._parse_prev_docs(response)
        for meeting_name, meeting_date in prev_meeting_docs:
            data = self._set_meeting_defaults(response, meeting_name)
            data['start'] = {'date': meeting_date.date(), 'time': None, 'note': ''}
            data['documents'] = prev_meeting_docs[(meeting_name, meeting_date)]
            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)
            yield data

    def _parse_prev_docs(self, response):
        docs = defaultdict(list)
        links = response.css('li.linksGroup-item a').xpath('self::*[contains(span, "DBRA")]')
        for link in links:
            link_text = link.xpath("span/text()").extract_first('')
            is_date = self._parse_date(link_text)
            if is_date:
                name = self._get_meeting_name(link_text, is_date.group(1))
                if name is None:
                    continue
                dt = parse(is_date.group(1), fuzzy=True)
                document = self._create_document(link)
                docs[(name, dt)].append(document)
        return docs

    def _create_document(self, link):
        link_text = link.xpath('span/text()').extract_first('')
        date = self._parse_date(link_text).group(1)
        desc = link_text.split(date)[-1]
        url = link.xpath("@href").extract_first('')
        if 'AGENDA' in desc.upper():
            return {'url': url, 'note': 'agenda'}
        if 'MINUTES' in desc.upper():
            return {'url': url, 'note': 'minutes'}
        return {'url': url, 'note': desc.lower().strip()}

    @staticmethod
    def _parse_date(text):
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        return date_regex.search(text)

    def _set_meeting_defaults(self, response, name):
        classification = self._set_classification(name)
        data = {
            '_type': 'event',
            'name': name,
            'event_description': '',
            'classification': classification,
            'end': {'date': None, 'time': None, 'note': ''},
            'all_day': False,
            'location': {
                'neighborhood': '',
                'name': 'DEGC, Guardian Building',
                'address': '500 Griswold, Suite 2200, Detroit'
            },
            'documents': [],
            'sources': [{'url': response.url, 'note': ''}]
        }
        return data

    @staticmethod
    def _parse_time(date_time_text):
        time_regex = re.compile(r'((1[012]|[1-9]):([0-5][0-9])\s?[ap].?m\.?)', flags=re.IGNORECASE)
        time_text = time_regex.findall(date_time_text)
        return time_text

    @staticmethod
    def _get_meeting_name(link_text, date_text):
        name = link_text.split(date_text)[0].strip()
        if name == 'DBRA':
            return 'Board of Directors'
        if name == 'DBRA CAC':
            return 'Community Advisory Committee'
        return None

    @staticmethod
    def _set_classification(name):
        if name.upper() == 'BOARD OF DIRECTORS':
            return BOARD
        if name.upper() == 'COMMUNITY ADVISORY COMMITTEE':
            return ADVISORY_COMMITTEE
        return NOT_CLASSIFIED
