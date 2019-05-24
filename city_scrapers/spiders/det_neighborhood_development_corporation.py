import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetNeighborhoodDevelopmentCorporationSpider(CityScrapersSpider):
    name = 'det_neighborhood_development_corporation'
    agency = 'Detroit Neighborhood Development Corporation'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/ndc/']

    def parse(self, response):
        yield from self._next_meeting(response)
        # some previous meetings are posted on the first page
        # with their agenda only, while others are on next page
        # in a similar format
        yield from self._first_page_prev_meetings(response)
        yield from self._next_page_prev_meetings(response)

    def _next_meeting(self, response):
        next_meeting_text = ' '.join(response.css('.content-itemContent *::text').extract())
        start_time = self._parse_next_start_time(next_meeting_text)
        for meeting_start in re.findall(
            r'[a-zA-Z]{3,10}\s+\d{1,2},?\s+\d{4}.*?(?=\.)', next_meeting_text
        ):
            meeting = self._set_meeting_defaults(response)
            meeting['start'] = self._parse_next_start(meeting_start, start_time)
            meeting['status'] = self._get_status(meeting, text=meeting_start)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _next_page_prev_meetings(self, response):
        prev_meetings_xpath = '//a[contains(., "Past")]'
        prev_meetings = response.xpath(prev_meetings_xpath)
        for a in prev_meetings:
            yield response.follow(a, callback=self._parse_prev_meetings)

    def _first_page_prev_meetings(self, response):
        other_prev_meetings = response.xpath("//a[contains(., 'Board')]")
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

    @staticmethod
    def _parse_next_start_time(text):
        time_str = re.search(r'\d{1,2}:\d{1,2}\s*[apmAPM\.]{2,4}', text).group()
        return datetime.strptime(re.sub(r'[\.\s]', '', time_str).upper(), '%I:%M%p').time()

    @staticmethod
    def _parse_next_start(date_text, time_obj):
        date_str = re.search(r'\w{3,10}\s+\d{1,2},?\s+\d{4}', date_text).group().replace(',', '')
        date_obj = datetime.strptime(date_str, '%B %d %Y').date()
        return datetime.combine(date_obj, time_obj)

    def _parse_start(self, date_time_text):
        time_match = self._parse_time(date_time_text)
        date_match = self._parse_date(date_time_text)
        try:
            return parse(date_match.group(1) + ' ' + time_match.group(1), fuzzy=True)
        except ValueError:
            pass

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
