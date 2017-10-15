# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import pytz
import scrapy

from datetime import date, datetime, timedelta


class PbccSpider(scrapy.Spider):
    name = 'pbcc'
    long_name = 'Public Building Commission of Chicago'
    allowed_domains = ['www.pbcchicago.com']
    base_url = 'http://www.pbcchicago.com/content/about/calendar.asp'
    calendar_date = datetime.now()
    start_urls = ['{}?myDate={}'.format(
        base_url, calendar_date.strftime('%m/%d/%Y')
    )]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for cal_day in response.css('td.calday2'):
            cal_number = cal_day.xpath("./div[contains(@class, 'calnumber')]/text()").extract_first()
            if not cal_number:
                continue
            cal_date = date(self.calendar_date.year, self.calendar_date.month, int(cal_number))
            for item in cal_day.xpath("./div[not(contains(@class, 'calnumber'))]"):
                # Ignore holidays added to calendar
                if item.css('a b::text').extract_first().strip() != 'Holiday':
                    yield {
                        '_type': 'event',
                        'id': self._parse_id(item),
                        'name': self._parse_name(item, cal_date),
                        'description': self._parse_description(item),
                        'classification': self._parse_classification(item),
                        'start_time': self._parse_start(item, cal_date),
                        'end_time': None,
                        'all_day': self._parse_all_day(item),
                        'status': self._parse_status(item),
                        'location': self._parse_location(item),
                        'sources': self._parse_sources(item)
                    }

        # Add 30 days to the current date, stop if more than 180 days (~6 months) ahead
        self.calendar_date += timedelta(days=30)
        if (self.calendar_date - datetime.now()).days <= 180:
            yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.

        The parse method updates the calendar_date property,
        so create a query param from that.
        """
        next_url = '{}?myDate={}'.format(
            self.base_url,
            self.calendar_date.strftime('%m/%d/%Y')
        )
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.

        All links for PBCC appear to include eID or BID_ID, so raise an error
        if not found rather than creating a slug.
        """
        event_link = item.css('a::attr(href)').extract_first()
        if '?eID=' in event_link:
            id_suffix = event_link.split('?eID=')[-1]
        elif '?BID_ID=' in event_link:
            id_suffix = event_link.split('?BID_ID=')[-1]
        else:
            raise ValueError('ID is required and not present in eID or BID_ID params')
        return 'PBCC{}'.format(id_suffix)

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).

        PBCC has relatively helpful classifications, expanding the AFB acronym.
        """
        classification = item.css('a b::text').extract_first().strip()
        if classification == 'AFB':
            return 'Advertisement for Bids'
        else:
            return classification

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.

        TODO: Location details are inconsistent across event types, addresses
        are mixed up with names and neither are reliably in the same place.
        Could make manual exceptions for board meetings, or go to sub-page
        """
        return {
            'url': None,
            'name': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.

        Returns True if _parse_start_time is None
        """
        return self._parse_start_time(item) is None

    def _parse_name(self, item, cal_date):
        """
        Parse or generate event name.
        """
        name_str = ''.join(item.xpath('./text()').extract()).rstrip().strip()
        # Return without the beginning and end parentheses, additional spaces
        # inside of them removed as well
        clean_name_str = name_str[1:-1].strip()
        if clean_name_str:
            return '{} - {}'.format(self._parse_classification(item), clean_name_str)
        else:
            return '{} {}'.format(
                self._parse_classification(item),
                cal_date.strftime('%m/%d/%Y')
            )

    def _parse_description(self, item):
        """
        Parse or generate event name.

        Other than the page-long info on AFBs, there isn't much of a description for
        events outside of the classification and name, so returning None. Could be
        implemented later for AFBs
        """
        return None

    def _parse_start(self, item, cal_date):
        """
        Parse start date and time.

        Returns the date at midnight if no time provided.
        """
        start_time = self._parse_start_time(item)
        if start_time:
            start_datetime = datetime.combine(cal_date, start_time)
        else:
            start_datetime = datetime.combine(cal_date, datetime.min.time())
        tz = pytz.timezone('America/Chicago')
        return tz.localize(start_datetime).isoformat()

    def _parse_start_time(self, item):
        """
        Returns a datetime.time object if found in regex search, otherwise none

        Element structure is inconsistent, so search full text.
        """
        item_text = ''.join(item.xpath('.//text()').extract())
        time_str = re.search(r'\d{1,2}:\d{2}(AM|PM)', item_text)
        if not time_str:
            return None
        else:
            return datetime.strptime(time_str.group(0), '%I:%M%p').time()

    def _parse_sources(self, item):
        """
        Parse source from base URL and event link
        """
        return [{
            'url': 'http://www.pbcchicago.com' + item.css('a::attr(href)').extract_first()
        }]
