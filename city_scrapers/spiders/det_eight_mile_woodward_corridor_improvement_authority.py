# -*- coding: utf-8 -*-
import re
from collections import defaultdict

from dateutil.parser import parse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class DetEightMileWoodwardCorridorImprovementAuthoritySpider(Spider):
    name = 'det_eight_mile_woodward_corridor_improvement_authority'
    agency_name = 'Detroit Eight Mile Woodward Corridor Improvement Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/emwcia/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        yield from self._prev_meetings(response)

        next_board_meeting_xpath = '//p[.//text()[contains(., "The next Regular Board meeting is")]]//text()'
        next_board_text = ' '.join(response.xpath(next_board_meeting_xpath).extract())
        data = self._set_meeting_defaults(response)
        data['start'] = self._parse_start(next_board_text)
        data['status'] = self._generate_status(data, text='')
        data['id'] = self._generate_id(data)

        yield data

    def _prev_meetings(self, response):
        past_meetings_xpath = '//a[span/text()="Past Agendas and Minutes"]'
        past_meetings = response.xpath(past_meetings_xpath)
        for a in past_meetings:
            yield response.follow(a, callback=self._parse_previous)

    @staticmethod
    def _set_meeting_defaults(response):
        data = {
            '_type': 'event',
            'name': 'Board of Directors',
            'event_description': '',
            'classification': BOARD,
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
    def _parse_start(date_time_text):
        # time + date are spread out in text, so find them with regex
        # and use parse to convert / validate
        time_regex = re.compile(r'((1[0-2]|0?[1-9]):([0-5]?[0-9])( ?[AP]M)?)')
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        t = time_regex.search(date_time_text)
        d = date_regex.search(date_time_text)
        try:
            dt = parse(d.group(1) + " " + t.group(1), fuzzy=True)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': ''}

    def _parse_previous(self, response):
        docs = self._parse_prev_docs(response)
        for meeting_date in docs:
            data = self._set_meeting_defaults(response)
            data['start'] = {'date': meeting_date.date(), 'time': None, 'note': ''}
            data['documents'] = docs[meeting_date]
            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)
            yield data

    def _parse_prev_docs(self, response):
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        non_empty_li = response.css('li.linksGroup-item').xpath('self::*[a]')
        docs = defaultdict(list)
        for li in non_empty_li:
            full_text = li.xpath("a/span/text()").extract_first('')
            link = li.xpath("a/@href").extract_first('')
            date_text = date_regex.search(full_text).group(1)
            dt = parse(date_text, fuzzy=True)
            if 'AGENDA' in full_text.upper():
                docs[dt].append({'url': link, 'note': 'agenda'})
            elif 'MINUTES' in full_text.upper():
                docs[dt].append({'url': link, 'note': 'minutes'})
            else:
                docs[dt].append({'url': link, 'note': ''})
        return docs
