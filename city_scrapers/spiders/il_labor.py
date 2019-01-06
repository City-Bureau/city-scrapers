# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import timedelta

from dateutil.parser import parse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class IlLaborSpider(Spider):
    name = 'il_labor'
    agency_name = 'Illinois Labor Relations Board'
    allowed_domains = ['www2.illinois.gov']
    start_urls = ['https://www2.illinois.gov/ilrb/meetings/Pages/default.aspx']
    event_timezone = 'America/Chicago'
    """
    This page only lists the next upcoming meeting for each of the three boards.
    All other meetingd dates are `proposed` and only available via PDF.
    """

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        for item in response.css('.soi-article-content .container > .row > p'):
            """
            Some monthly meetings are skipped. Instead of providing a date,
            there's text that says 'No /name/ meeting in month'.
            If the date/time info can't be parsed, assume that it is a `no meeting`
            notice.
            """
            start_datetime = self._parse_start(item)
            if start_datetime is None:
                continue

            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'event_description': self._parse_description(response),
                'classification': BOARD,
                'start': {
                    'date': start_datetime.date(),
                    'time': start_datetime.time()
                },
                'end': {
                    'date': start_datetime.date(),
                    'time': (start_datetime + timedelta(hours=3)).time()
                },
                'all_day': False,
                'timezone': self.event_timezone,
                'location': self._parse_location(item),
                'sources': self._parse_sources(response),
                'documents': self._parse_documents(item),
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data)
            yield data

    def _parse_location(self, item):
        """
        Get address from the next paragraph following the event item.
        Note: the structure of the page is not consistent. Usually the
        next row contains the meeting time, but sometimes
        multiple meeting locations are listed within a single div.
        """
        addr_in_row = item.xpath('following-sibling::*//p/text()')
        addr_next_row = item.xpath('../following-sibling::div[1]//p/text()')
        address_list = addr_in_row if len(addr_in_row) > 0 else addr_next_row
        chi_address_list = [
            addr.replace('\xa0', '').strip()
            for addr in address_list.extract()
            if 'chicago' in addr.lower()
        ]
        return {'url': '', 'address': chi_address_list[0], 'name': ''}

    def _parse_name(self, item):
        """
        Get event name from the first `<strong>`.
        """
        name = item.css('a::text').extract_first()
        if name:
            return name.title()
        return item.css('strong::text').extract_first().title()

    def _parse_description(self, response):
        """
        No meeting-specific description, so use a generic description from page.
        """
        return response.css('#ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField p::text'
                            ).extract_first().strip()

    def _parse_start(self, item):
        """
        Parse start date and time from the second `<strong>`
        """
        try:
            dt_str = item.css('strong:nth-of-type(2)::text').extract_first()
            if not dt_str:
                dt_str = item.css('strong:nth-of-type(3)::text').extract_first()
            return parse(dt_str or '')
        except ValueError:
            return None

    def _parse_documents(self, item):
        href = item.css('a::attr(href)').extract_first()
        if href:
            return [{'url': 'https://{}{}'.format(self.allowed_domains[0], href), 'note': 'Agenda'}]
        return []

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
