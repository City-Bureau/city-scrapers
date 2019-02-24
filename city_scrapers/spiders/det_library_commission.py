import re
from datetime import datetime, timedelta
from urllib.parse import unquote

from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class DetLibraryCommissionSpider(CityScrapersSpider):
    name = 'det_library_commission'
    agency = 'Detroit Public Library'
    timezone = 'America/Detroit'
    allowed_domains = ['detroitpubliclibrary.org']

    @property
    def start_urls(self):
        """Pull events from the calendar pages for 2 months past through 2 months ahead"""
        now = datetime.now()
        urls = []
        for months_delta in range(-2, 3):
            month_str = (now + relativedelta(months=months_delta)).strftime("%m/%Y")
            urls.append("https://detroitpubliclibrary.org/events/commission/{}".format(month_str))
        return urls

    def parse(self, response):
        """Yields requests for each meeting found in the calendar"""
        for link in response.css('#month_calendar .event a::attr(href)'):
            yield response.follow(link.extract(), self._parse_item)

    def _parse_item(self, response):
        """`_parse_item` should always `yield` Meeting items"""
        start = self._parse_start(response)
        end, has_end = self._parse_end(response, start)
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description='',
            classification=self._parse_classification(title),
            start=start,
            end=end,
            time_notes='' if has_end else 'End estimated 3 hours after start time',
            all_day=False,
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting['id'] = self._get_id(meeting)
        meeting['status'] = self._get_status(meeting)
        return meeting

    def _parse_start(self, response):
        """Parse start datetime from time element"""
        start_dt_str = response.css('time::attr(datetime)').extract_first()[:16]
        return datetime.strptime(start_dt_str, '%Y-%m-%dT%H:%M')

    def _parse_end(self, response, start):
        """Parse end datetime from duration string"""
        duration_str = response.css('tr:nth-child(2) th[scope="row"] + td::text').extract_first()
        if not duration_str or ' - ' not in duration_str:
            return start + timedelta(hours=3), False
        end_str = duration_str.split(' - ')[-1]
        end_time = datetime.strptime(end_str, '%I:%M%p').time()
        return datetime.combine(start.date(), end_time), True

    @staticmethod
    def _parse_title(response):
        return response.css('main header h1::text').extract_first().strip()

    @staticmethod
    def _parse_classification(title):
        if 'committee' in title.lower():
            return COMMITTEE
        return COMMISSION

    @staticmethod
    def _parse_location(response):
        """Parse location from JS variable in page"""
        script_contents = response.css('script[type="text/javascript"]::text').extract_first()
        addr_str = unquote(
            re.search(r'(?<=destination=).*(?=\';)', script_contents).group(),
        ).replace('\n', ' ')
        loc_name_str = response.css('tr:nth-child(3) th[scope="row"] + td a::text').extract_first()
        return {
            'name': loc_name_str,
            'address': addr_str,
        }

    def _parse_links(self, response):
        """Parse meeting links from page"""
        links = []
        for link_block in response.css('section[data-block-type="document-list"] li'):
            title = link_block.css('article h3 > span:last-child::text').extract_first()
            links.append({
                'title': title.strip(),
                'href': link_block.css('a::attr(href)').extract_first(),
            })
        return links
