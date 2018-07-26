# -*- coding: utf-8 -*-
import re
from collections import defaultdict

from dateutil.parser import parse

from city_scrapers.spider import Spider


class DetDowntownDevelopmentAuthoritySpider(Spider):
    name = 'det_downtown_development_authority'
    agency_id = 'Downtown Development Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/dda/']

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
        next_meeting_xpath = '//text()[contains(., "The next Regular DDA Board meeting is")]'
        next_meeting_text = ' '.join(response.xpath(next_meeting_xpath).extract())
        data = self._set_meeting_defaults(response)
        data['start'] = self._parse_start(next_meeting_text)
        data['documents'] = self._parse_docs(response, data['start']['date'])
        data['status'] = self._generate_status(data, text='')
        data['id'] = self._generate_id(data)
        yield data

    def _prev_meetings(self, response):
        prev_meetings_xpath = '//a[contains(., "Agendas and Minutes")]'
        prev_meetings = response.xpath(prev_meetings_xpath)
        for a in prev_meetings:
            yield response.follow(a, callback=self._parse_prev_meetings)

    @staticmethod
    def _parse_start(date_time_text):
        try:
            dt = parse(date_time_text, fuzzy=True)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': ''}

    def _parse_prev_meetings(self, response):
        # there are only documents for prev meetings,
        # so use these to create prev meetings
        prev_meeting_docs = self._parse_prev_docs(response)
        for meeting_date in prev_meeting_docs:
            data = self._set_meeting_defaults(response)
            data['start'] = {'date': meeting_date.date(), 'time': None, 'note': ''}
            data['documents'] = prev_meeting_docs[meeting_date]
            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)
            yield data

    def _parse_prev_docs(self, response):
        docs = defaultdict(list)
        links = response.css('li.linksGroup-item a')
        for link in links:
            link_text = link.xpath("span/text()").extract_first('')
            is_date = self._parse_date(link_text)
            if is_date:
                dt = parse(is_date.group(1), fuzzy=True)
                document = self._create_document(link)
                docs[dt].append(document)
        return docs

    def _parse_docs(self, response, meeting_date):
        docs = []
        doc_links = response.xpath("//a[span/text()[contains(., 'Agenda')]]")
        for link in doc_links:
            # meeting details and docs are in separate places,
            # so find the docs that match meeting_date
            if self._matches_meeting_date(link, meeting_date):
                document = self._create_document(link)
                docs.append(document)
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

    def _matches_meeting_date(self, link, meeting_date):
        link_text = link.xpath('span/text()').extract_first('')
        if self._parse_date(link_text):
            agenda_date = parse(link_text, fuzzy=True)
            if agenda_date.date() == meeting_date:
                return True
        return False

    @staticmethod
    def _parse_date(text):
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        return date_regex.search(text)

    @staticmethod
    def _set_meeting_defaults(response):
        data = {
            '_type': 'event',
            'name': 'Board of Directors',
            'event_description': '',
            'classification': 'Board',
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
