import re
from collections import defaultdict

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, FORUM, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetBrownfieldRedevelopmentAuthoritySpider(CityScrapersSpider):
    name = 'det_brownfield_redevelopment_authority'
    agency = 'Detroit Brownfield Redevelopment Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/dbra/']
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226',
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting_link_xpath = '//a[contains(., "Minutes")]'
        self._validate_location(response)
        meeting_links = response.xpath(meeting_link_xpath)
        for a in meeting_links:
            yield response.follow(a, callback=self._parse_meetings)

    def _parse_meetings(self, response):
        meeting_link_map = self._parse_meeting_links(response)
        for title, date_text in meeting_link_map.keys():
            classification = self._parse_classification(title)
            meeting = Meeting(
                title=title,
                description='',
                classification=classification,
                start=self._parse_start(date_text, classification),
                end=None,
                time_notes=self._parse_time_notes(classification),
                all_day=False,
                location=self.location,
                links=meeting_link_map[(title, date_text)],
                source=response.url,
            )
            # Check if there's a cancellation notice to help determine status
            meeting['status'] = self._get_status(
                meeting, text=' '.join([l['title'] for l in meeting_link_map[(title, date_text)]])
            )
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_start(self, dt, classification):
        if classification == BOARD:
            dt = dt.replace(hour=16)
        elif classification == ADVISORY_COMMITTEE:
            dt = dt.replace(hour=17)
        return dt

    def _parse_meeting_links(self, response):
        docs = defaultdict(list)
        links = response.css('li.linksGroup-item a')
        for link in links:
            link_text = link.xpath("span/text()").extract_first('')
            if not link_text:
                continue
            is_date = self._parse_date(link_text)
            if is_date:
                title = self._parse_title(link_text)
                if title is None:
                    continue
                dt = parse(is_date.group(1), fuzzy=True)
                document = self._create_document(link)
                docs[(title, dt)].append(document)
        return docs

    def _create_document(self, link):
        link_text = link.xpath('span/text()').extract_first('')
        date_str = self._parse_date(link_text).group(1)
        link_title = ' '.join(link_text.split(date_str))
        url = link.xpath("@href").extract_first('')
        if 'AGENDA' in link_title.upper():
            return {'href': url, 'title': 'Agenda'}
        if 'MINUTES' in link_title.upper():
            return {'href': url, 'title': 'Minutes'}
        return {'href': url, 'title': re.sub(r'\s+', ' ', link_title).strip()}

    @staticmethod
    def _parse_date(text):
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        return date_regex.search(text)

    @staticmethod
    def _parse_time_notes(classification):
        if classification not in [BOARD, ADVISORY_COMMITTEE]:
            return 'See source for meeting time'
        return ''

    @staticmethod
    def _parse_title(link_text):
        if 'Committee' in link_text:
            return '{} Committee'.format(link_text.split(' Committee')[0]).replace('DBRA ', '')
        elif 'Public Hearing' in link_text:
            return '{} Public Hearing'.format(link_text.split(' Public Hearing')[0])
        elif re.match(r'DBRA[\- ]CAC', link_text):
            return 'Community Advisory Committee'
        elif 'DBRA' in link_text:
            return 'Board of Directors'
        return None

    @staticmethod
    def _parse_classification(title):
        if title.upper() == 'BOARD OF DIRECTORS':
            return BOARD
        if title.upper() == 'COMMUNITY ADVISORY COMMITTEE':
            return ADVISORY_COMMITTEE
        if 'COMMITTEE' in title.upper():
            return COMMITTEE
        if 'HEARING' in title.upper():
            return FORUM
        return NOT_CLASSIFIED

    @staticmethod
    def _validate_location(response):
        description = ' '.join(response.css('.content-itemContent *::text').extract())
        if '500 Griswold' not in description:
            raise ValueError('Meeting location no longer appears in description')
