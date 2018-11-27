"""
-I'm able to get the start times for the past meetings. What else should I add?
"""

# -*- coding: utf-8 -*-
from city_scrapers.spider import Spider
from city_scrapers.constants import COMMISSION
from datetime import datetime
import re


class ChiBoardElectionsSpider(Spider):
    name = 'chi_board_elections'
    agency_name = 'Chicago Board of Elections'
    timezone = 'America/Chicago'
    allowed_domains = ['chicagoelections.com']
    start_urls = ['https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        yield from self._prev_meetings(response)
        yield from self._next_meeting(response)

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _next_meeting(self, response):
        next_meeting = response.xpath('//div[@class="copy"]/text()').extract()[2]
        meetingdate = re.search(r'\d{1}:.{24}', next_meeting).group(0)
        data = {
            '_type': 'event',
            'name': "Chicago Board of Election Commissioners",
            'event_description': "Meeting",
            'classification': COMMISSION,
            'start': self._parse_start(meetingdate),
            'end': {},
            'all_day': False,
            'location': self._parse_location(response),
            'documents': [],
            'sources': [{
                    'url': response.url,
                    'note': ''
                }],
        }

        data['status'] = self._generate_status(data)
        data['id'] = self._generate_id(data)
        yield data

    def _prev_meetings(self, response):
        meetings = response.xpath("//a/text()").extract()
        meetingdates = [meeting[22:] for meeting in meetings if "Minutes" not in meeting]
        for meetingdate in meetingdates:
            meetingdate = "9:30 a.m. on " + meetingdate
            data = {
                '_type': 'event',
                'name': "Chicago Board of Election Commissioners",
                'event_description': "Meeting",
                'classification': COMMISSION,
                'start': self._parse_start(meetingdate),
                'end': {},
                'all_day': False,
                'location': self._parse_location(response),
                'documents': [],
                'sources': [{
                    'url': response.url,
                    'note': ''
                }],
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return ''

    def _parse_description(self, item):
        """
        Parse or generate event description.
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
        datetime_item = datetime.strptime(formatitem, '%I:%M %p on %b. %d, %Y')
        dict = {'date': datetime_item.date(), 'time': datetime_item.time(), 'note': ''}
        return dict


    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return ''

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

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

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': '', 'note': ''}]
