# -*- coding: utf-8 -*-
import re
from datetime import datetime

import scrapy

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiBoardElectionsSpider(Spider):
    name = 'chi_board_elections'
    agency_name = 'Chicago Board of Elections'
    timezone = 'America/Chicago'
    allowed_domains = ['chicagoelections.com']
    start_urls = [
        'https://app.chicagoelections.com/pages/en/board-meetings.aspx',
        'https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx'
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        if "minutes" in response.url:  # Current meetings and past meetings on differerent pages
            yield from self._prev_meetings(response)
        else:
            yield from self._next_meeting(response)

    def _next_meeting(self, response):
        next_meeting = response.xpath('//div[@class="copy"]/text()').extract()[2]
        meetingdate = re.search(r'\d{1,2}:.*\d{4}', next_meeting).group(0)
        data = {
            '_type': 'event',
            'name': "Electoral Board",
            'event_description': "",
            'classification': COMMISSION,
            'start': self._parse_start(meetingdate),
            'all_day': False,
            'location': self._parse_location(response),
            'documents': [],
            'sources': [{
                'url': response.url,
                'note': ''
            }],
        }
        data['end'] = {
            'date': data['start']['date'],
            'time': None,
            'note': '',
        }
        data['status'] = self._generate_status(data)
        data['id'] = self._generate_id(data)
        yield data

    def _prev_meetings(self, response):
        meetings = response.xpath("//a/text()").extract()
        meetingdates = [
            meeting[22:]
            for meeting in meetings
            if "Minutes" not in meeting and "mode" not in meeting and meeting is not " "
        ]
        for meetingdate in meetingdates:
            meetingdate = "9:30 a.m. on " + meetingdate
            data = {
                '_type': 'event',
                'name': "Electoral Board",
                'event_description': "",
                'classification': COMMISSION,
                'start': self._parse_start(meetingdate),
                'all_day': False,
                'location': self._parse_location(response),
                'documents': [],
                'sources': [{
                    'url':
                        response.url,
                    'note': ''
                }],
            }
            data['end'] = {
                'date': data['start']['date'],
                'time': None,
                'note': '',
            }
            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return ''

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return ''

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        formatitem = item.replace("a.m.", "AM")
        formatitem = formatitem.replace("p.m.", "PM")
        formatitem = formatitem.replace("Sept", "Sep")
        try:
            datetime_item = datetime.strptime(formatitem, '%I:%M %p on %b. %d, %Y')
        except ValueError:  # Some months are abbreviated, some are not
            datetime_item = datetime.strptime(formatitem, '%I:%M %p on %B %d, %Y')
        dict = {'date': datetime_item.date(), 'time': datetime_item.time(), 'note': ''}
        return dict

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': '8th Floor Office, 69 W. Washington St.',
            'name': 'Cook County Administration Building',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        return [{'url': '', 'note': ''}]
