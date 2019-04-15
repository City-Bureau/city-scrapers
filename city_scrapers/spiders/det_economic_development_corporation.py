import re
from collections import defaultdict

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetEconomicDevelopmentCorporationSpider(CityScrapersSpider):
    name = 'det_economic_development_corporation'
    agency = 'Detroit Economic Development Corporation'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/edc/']

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        yield from self._prev_meetings(response)
        yield from self._next_meeting(response)

    def _next_meeting(self, response):
        next_meeting_xpath = ('//p[contains(., "The next Regular Board meeting is")]//text()')
        next_meeting_text = ' '.join(response.xpath(next_meeting_xpath).extract())
        meeting = self._set_meeting_defaults(response)
        meeting['start'] = self._parse_start(next_meeting_text)
        if meeting['start']:
            meeting['links'] = []
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _prev_meetings(self, response):
        prev_meetings_xpath = '//a[contains(., "Agendas and Minutes")]'
        prev_meetings = response.xpath(prev_meetings_xpath)
        for a in prev_meetings:
            yield response.follow(a, callback=self._parse_prev_meetings)

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

    def _parse_time(self, date_time_text):
        time_regex = re.compile(r'((1[012]|[1-9]):([0-5][0-9])\s?[ap].?m\.?)')
        time_text = time_regex.search(date_time_text, re.IGNORECASE)
        return time_text

    def _parse_prev_meetings(self, response):
        # there are only documents for prev meetings,
        # so use these to create prev meetings
        prev_meeting_docs = self._parse_prev_docs(response)
        for meeting_date in prev_meeting_docs:
            meeting = self._set_meeting_defaults(response)
            meeting['start'] = meeting_date
            meeting['links'] = prev_meeting_docs[meeting_date]
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_prev_docs(self, response):
        docs = defaultdict(list)
        links = response.css('li.linksGroup-item a')
        for link in links:
            link_text = link.xpath("span/text()").extract_first('')
            is_date = self._parse_date(link_text)
            if is_date:
                dt = parse(is_date.group(1), fuzzy=True)
                document = self._create_link(link)
                docs[dt].append(document)
        return docs

    def _create_link(self, link):
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
                'address': '500 Griswold St, Suite 2200, Detroit, MI 48226'
            },
            links=[],
            source=response.url,
        )
