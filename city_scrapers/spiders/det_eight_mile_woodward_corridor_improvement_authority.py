import re
from collections import defaultdict

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetEightMileWoodwardCorridorImprovementAuthoritySpider(CityScrapersSpider):
    name = 'det_eight_mile_woodward_corridor_improvement_authority'
    agency = 'Detroit Eight Mile Woodward Corridor Improvement Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['www.degc.org']
    start_urls = ['http://www.degc.org/public-authorities/emwcia/']

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        yield from self._prev_meetings(response)

        next_board_meeting_xpath = (
            '//p[.//text()[contains(., "The next Regular Board meeting is")]]//text()'
        )
        next_board_text = ' '.join(response.xpath(next_board_meeting_xpath).extract())
        meeting = self._set_meeting_defaults(response)
        meeting['start'] = self._parse_start(next_board_text)
        meeting['status'] = self._get_status(meeting)
        meeting['id'] = self._get_id(meeting)
        yield meeting

    def _prev_meetings(self, response):
        past_meetings_xpath = '//a[span/text()="Past Agendas and Minutes"]'
        past_meetings = response.xpath(past_meetings_xpath)
        for a in past_meetings:
            yield response.follow(a, callback=self._parse_previous)

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

    @staticmethod
    def _parse_start(date_time_text):
        # time + date are spread out in text, so find them with regex
        # and use parse to convert / validate
        time_regex = re.compile(r'((1[0-2]|0?[1-9]):([0-5]?[0-9])( ?[AP]M)?)')
        date_regex = re.compile(r'([A-z]+ [0-3]?[0-9], \d{4})')
        t = time_regex.search(date_time_text)
        d = date_regex.search(date_time_text)
        try:
            return parse(d.group(1) + " " + t.group(1), fuzzy=True)
        except ValueError:
            pass

    def _parse_previous(self, response):
        docs = self._parse_prev_docs(response)
        for meeting_date in docs:
            meeting = self._set_meeting_defaults(response)
            meeting['start'] = meeting_date
            meeting['links'] = docs[meeting_date]
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

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
                docs[dt].append({'href': link, 'title': 'Agenda'})
            elif 'MINUTES' in full_text.upper():
                docs[dt].append({'href': link, 'title': 'Minutes'})
            else:
                docs[dt].append({'href': link, 'title': ''})
        return docs
