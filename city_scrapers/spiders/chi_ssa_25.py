# -*- coding: utf-8 -*-
import re
from datetime import datetime

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiSsa25Spider(Spider):
    name = 'chi_ssa_25'
    agency_name = 'Chicago Special Service Area #25 Little Village'
    timezone = 'America/Chicago'
    allowed_domains = ['littlevillagechamber.org']
    start_urls = [
        'http://littlevillagechamber.org/{}-meetings-minutes/'.format(datetime.now().year)
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        in_meeting_rows = False
        for item in response.css('table tr'):
            is_meeting_row = len(item.css('td:not([bgcolor])')) > 0
            if not in_meeting_rows and is_meeting_row:
                in_meeting_rows = True
            if in_meeting_rows and not is_meeting_row:
                break
            elif not is_meeting_row:
                continue
            date_str, time_str = self._parse_date_time_str(item)
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': '',
                'classification': COMMISSION,
                'start': self._parse_start(date_str, time_str),
                'end': self._parse_end(date_str, time_str),
                'all_day': False,
                'location': self._parse_location(item),
                'documents': self._parse_documents(item),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }],
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        meeting_type = item.css('td::text').extract()[4]
        return 'Commission: {}'.format(meeting_type)

    def _parse_date_time_str(self, item):
        """Pull out date and time strings"""
        date_str = item.css('td::text').extract()[1]
        time_str = item.css('td::text').extract()[2]
        return date_str, time_str

    def _parse_start(self, date_str, time_str):
        """
        Parse start date and time.
        """
        duration_str, am_pm = time_str.split(' ')
        start_time_str = duration_str.split('-')[0]
        return {
            'date': datetime.strptime(date_str, '%m/%d/%Y').date(),
            'time': datetime.strptime('{} {}'.format(start_time_str, am_pm), '%I:%M %p').time(),
            'note': '',
        }

    def _parse_end(self, date_str, time_str):
        """
        Parse end date and time.
        """
        duration_str, am_pm = time_str.split(' ')
        end_time_str = duration_str.split('-')[-1]
        return {
            'date': datetime.strptime(date_str, '%m/%d/%Y').date(),
            'time': datetime.strptime('{} {}'.format(end_time_str, am_pm), '%I:%M %p').time(),
            'note': '',
        }

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        loc_text = item.css('td::text').extract()[3]
        loc_name = re.search(r'^[^\d]*(?=\d{2,4})', loc_text).group()
        loc_addr = loc_text[len(loc_name):]
        loc_name = loc_name.rstrip('-–, ')
        if 'Chicago' not in loc_addr:
            loc_addr += ' Chicago, IL'
        return {
            'address': loc_addr,
            'name': loc_name,
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        minutes_link = item.css('td a::attr(href)').extract_first()
        if minutes_link:
            return [{'url': minutes_link, 'note': 'Minutes'}]
        return []
