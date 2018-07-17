# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime, timedelta
from dateutil.parser import parse

from city_scrapers.spider import Spider


class Il_laborSpider(Spider):
    name = 'il_labor'
    long_name = 'Illinois Labor Relations Board'
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

        # There's not a lot of structure on this page, so this selector is pretty fragile
        for item in response.xpath("//div[@class='row']/p/strong[contains(text(), 'MEETING')]/../.."):
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
                'classification': self._parse_classification(item),
                'start': { 'date': start_datetime.date(), 'time': start_datetime.time() },
                'end': { 'date': start_datetime.date(), 'time': (start_datetime + timedelta(hours=3)).time() },
                'all_day': self._parse_all_day(item),
                'timezone': self.event_timezone,
                'status': self._parse_status(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(response),
                'documents': None
            }
            data['id'] = self._generate_id(data)
            yield data

    def _parse_classification(self, item):
        """
        These are `board meetings`, but set to `committee meeting` as specified
        in event schema
        """
        return 'committee-meeting'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        These meetings seem confirmed, but to follow default of other scrapers,
        set to `tentative`
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        Get address from the next paragraph following the event item.
        Note: the structure of the page is not consistent. Usually the
        next row contains the meeting time, but sometimes
        multiple meeting locations are listed within a single div.
        """
        childs_siblings = item.xpath('child::*')
        if len(childs_siblings) > 1:
            addresses = item.xpath('child::div/div/p/text()').extract()
            address = ' Or '.join([a.strip() for a in addresses])
        else:
            address = item.xpath('following-sibling::div[1]/div/p/text()').extract_first()
            if address:
                address = address.strip()

        return {
            'url': '',
            'address': address,
            'name': ''
        }

    def _parse_all_day(self, item):
        """
        It appears `all_day` is always false for these meetings.
        """
        return False

    def _parse_name(self, item):
        """
        Get event name from the first `<strong>`.
        """
        return item.css('strong::text').extract_first().capitalize()

    def _parse_description(self, response):
        """
        No meeting-specific description, so use a generic description from page.
        """
        return response.css('#ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField p::text').extract_first().strip()

    def _parse_start(self, item):
        """
        Parse start date and time from the second `<strong>`
        """
        try:
            return parse(item.css('strong:nth-of-type(2)::text').extract_first())
        except ValueError:
            return None

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
