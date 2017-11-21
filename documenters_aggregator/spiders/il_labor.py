# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime
from pytz import timezone

from documenters_aggregator.spider import Spider


class Il_laborSpider(Spider):
    name = 'il_labor'
    long_name = 'Illinois Labor Relations Board'
    allowed_domains = ['www.illinois.gov']
    start_urls = ['https://www.illinois.gov/ilrb/meetings/Pages/default.aspx']

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
        for item in response.css('.soi-article-content .row-fluid .span12>p:nth-child(odd)'):
            """
            Some monthly meetings are skipped. Instead of providing a date,
            there's text that says 'No /name/ meeting in month'.
            If the date/time info can't be parsed, assume that it is a `no meeting`
            notice.
            """
            start_time = self._parse_start(item)
            if start_time is None:
                continue
            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': start_time.isoformat() if start_time else None,
                'end_time': None,
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(item, data, start_time)
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
        Note: the structure of the page is not consistent. Sometimes the
        address is in the next sibling `<p>`,
        but it may be nested further down.
        So we select the next node first,
        then select the first `<p>` within it.
        """
        sibling = item.xpath('following-sibling::*')
        return {
            'url': None,
            'name': sibling.css('p::text').extract_first(),
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
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

    def _parse_description(self, item):
        """
        No meeting-specific description, so use a generic description from page.
        """
        return 'To discuss issues and cases pending before the panel'

    def _parse_start(self, item):
        """
        Parse start date and time from the second `<strong>`
        """
        time_string = item.css('strong:nth-of-type(2)::text').extract_first().replace('.', '')
        try:
            naive = datetime.strptime(time_string, '%A, %B %d, %Y at %I:%M %p')
            tz = timezone('America/Chicago')
            return tz.localize(naive)
        except ValueError:
            return None

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
