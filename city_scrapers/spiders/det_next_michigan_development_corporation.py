import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetNextMichiganDevelopmentCorporationSpider(CityScrapersSpider):
    name = 'det_next_michigan_development_corporation'
    agency = 'Detroit Next Michigan Development Corporation'
    timezone = 'America/Chicago'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/d-nmdc/']

    def parse(self, response):
        yield from self._next_meeting(response)
        # some previous meetings are posted on the first page
        # with their agenda only, while others are on next page
        # in a similar format
        yield from self._first_page_prev_meetings(response)
        yield from self._next_page_prev_meetings(response)

    def _next_meeting(self, response):
        next_meeting_text = ' '.join(response.css('.content-itemContent *::text').extract())
        meeting = self._set_meeting_defaults(response)
        meeting['start'] = self._parse_upcoming_start(next_meeting_text)
        if meeting['start']:
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _next_page_prev_meetings(self, response):
        prev_meetings_xpath = '//a[contains(., "Agendas and Minutes")]'
        prev_meetings = response.xpath(prev_meetings_xpath)
        for a in prev_meetings:
            yield response.follow(a, callback=self._parse_prev_meetings)

    def _first_page_prev_meetings(self, response):
        other_prev_meetings = response.xpath("//a[contains(., 'Agenda')]")
        other_prev_meetings = self._parse_prev_docs(other_prev_meetings)
        for meeting_date in other_prev_meetings:
            docs = other_prev_meetings[meeting_date]
            yield self._create_meeting_from_meeting_docs(meeting_date, docs, response)

    def _parse_prev_meetings(self, response):
        # there are only documents for prev meetings,
        # so use these to create prev meetings
        list_items = response.css('li.linksGroup-item a')
        prev_meeting_docs = self._parse_prev_docs(list_items)
        for meeting_date in prev_meeting_docs:
            docs = prev_meeting_docs[meeting_date]
            yield self._create_meeting_from_meeting_docs(meeting_date, docs, response)

    def _parse_start(self, date_time_text):
        time_match = self._parse_time(date_time_text)
        date_match = self._parse_date(date_time_text)
        try:
            if date_match and time_match:
                return parse(
                    '{} {}'.format(date_match.group(1), time_match.group(1)),
                    fuzzy=True,
                )
        except ValueError:
            pass

    def _parse_upcoming_start(self, text):
        date_str = re.search(r'\w{3,10}\s+\d{1,2},?\s+\d{4}', text).group()
        time_str = re.sub(
            r'([,\.]|\s+(?=[apAP])|)', '',
            re.findall(r'(?<=at\s)\s*\d{1,2}:\d{1,2}\s*[apmAPM\.]{2,4}', text)[-1]
        )
        return datetime.strptime(
            ' '.join([date_str, time_str]).replace(',', ''), '%B %d %Y %I:%M%p'
        )

    def _parse_time(self, date_time_text):
        time_regex = re.compile(r'((1[012]|[1-9]):([0-5][0-9])\s?[AP]M)')
        time_text = time_regex.search(date_time_text, re.IGNORECASE)
        return time_text

    def _create_meeting_from_meeting_docs(self, meeting_date, meeting_docs, response):
        meeting = self._set_meeting_defaults(response)
        meeting['start'] = meeting_date
        meeting['links'] = meeting_docs
        meeting['status'] = self._get_status(meeting)
        meeting['id'] = self._get_id(meeting)
        return meeting

    def _parse_prev_docs(self, links_selector):
        docs = defaultdict(list)
        for link in links_selector:
            link_text = link.xpath("span/text()").extract_first('')
            is_date = self._parse_date(link_text)
            if is_date:
                dt = parse(is_date.group(1), fuzzy=True)
                document = self._create_document(link)
                docs[dt].append(document)
        return docs

    def _create_document(self, link):
        link_text = link.xpath('span/text()').extract_first('')
        date = self._parse_date(link_text).group(1)
        desc = link_text.split(date)[-1]
        url = link.xpath("@href").extract_first('')
        if 'AGENDA' in desc.upper():
            return {'href': url, 'title': 'Agenda'}
        if 'MINUTES' in desc.upper():
            return {'href': url, 'title': 'Minutes'}
        return {'href': url, 'title': desc.strip()}

    @staticmethod
    def _parse_date(text):
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        return date_regex.search(text)

    @staticmethod
    def _set_meeting_defaults(response):
        return Meeting(
            title='Board of Directors',
            description='',
            classification=BOARD,
            end=None,
            time_notes='',
            all_day=False,
            location={
                'name': 'DEGC, Guardian Building',
                'address': '500 Griswold St, Suite 2200, Detroit, MI 48226',
            },
            links=[],
            source=response.url,
        )
