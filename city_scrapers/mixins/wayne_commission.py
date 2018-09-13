# THIS IS JUST A MIXIN. IT MAY USE THINGS THAT ARE NOT ACTUALLY USABLE YET,
# BUT IT WILL BE INTEGRATED INTO A REGULAR AGENCY SPIDER.

# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse as dateparse
from urllib.parse import urljoin

from city_scrapers.constants import CANCELED, COMMITTEE


class WayneCommissionMixin:
    timezone = 'America/Detroit'
    allowed_domains = ['www.waynecounty.com']
    classification = COMMITTEE
    location = {
        'name': '7th floor meeting room, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    }
    description = ''

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        for item in self._parse_entries(response):
            data = {
                '_type': 'event',
                'name': self.meeting_name,
                'event_description': self.description,
                'classification': self.classification,
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(item, response.url),
                'sources': [{'url': response.url, 'note': ''}]
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._parse_status(item, data)

            yield data

    def _parse_entries(self, response):
        return response.xpath('//tbody/tr[child::td/text()]')

    @staticmethod
    def _parse_documents(item, base_url):
        url = item.xpath('td/a/@href').extract_first()
        url = urljoin(base_url, url) if url is not None else ''
        if url != '':
            note = item.xpath('td/a/text()').extract_first()
            note = note.lower() if note is not None else ''
            return [{
                'url': url,
                'note': note
            }]
        return []

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Calendar shows only meetings in current year.
        yearStr = datetime.now().year
        # Dateparse can't always handle the inconsistent dates, so
        # let's normalize them using scrapy's regular expressions.
        month_str = item.xpath('.//td[2]/text()').re(r'[a-zA-Z]{3}')[0]
        day_str = item.xpath('.//td[2]/text()').re(r'\d+')[0]
        time_str = item.xpath('.//td[3]/text()').extract_first()
        date_str = dateparse('{0} {1} {2} {3}'.format(month_str, day_str, yearStr, time_str))

        return {'date': date_str.date(), 'time': date_str.time(), 'note': ''}

    def _parse_status(self, item, data):
        """
        Parse or generate status of meeting.
        Postponed meetings will be considered cancelled.
        """

        status_str = item.xpath('.//td[4]//text()').extract_first()
        # If the agenda column text contains "postpone" or "cancel" we consider it cancelled.
        if ('cancel' in status_str.lower()) or ('postpone' in status_str.lower()):
            return CANCELED
        # If it's not one of the above statuses, use the status logic from spider.py
        else:
            return self._generate_status(data, '')
