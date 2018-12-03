# -*- coding: utf-8 -*-
import re
from datetime import datetime

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
            'documents': [],
            'sources': [{
                'url': response.url,
                'note': ''
            }],
        }
        if "69" in next_meeting:
            data['location'] = self._parse_location(response)
        else:
            raise ValueError("The address has changed.")

        data['end'] = {
            'date': data['start']['date'],
            'time': None,
            'note': '',
        }

        link = response.xpath("//a/@href").extract_first()
        if link:
            data["documents"] = self._parse_documents(link)
        data['status'] = self._generate_status(data)
        data['id'] = self._generate_id(data)

        yield data

    def _prev_meetings(self, response):
        """
        If there's video in the entry, check that the last date doesn't match. If it doesn't, then enter.
        If video not in entry, then minutes in entry, if so extract date and data.
        -Hang up: How do I get data that doesn't use span?

         for meeting in meetings:
...     try:
...             meetingdates.append(re.search(r'(–|- |-)(.+[0-9]{4})', meeting).group(2))
...     except AttributeError:
...             continue
        """

        meetings = response.xpath("//a").extract()
        meetingdates = []
        prevdate = None
        for meeting in meetings:
            meeting.replace('\xa0', ' ')  # Gets rid of non-breaking space character
            try:
                meetingdate = re.search(r'(–|- |-)(.+[0-9]{4})', meeting).group(2)
                while len(meetingdate) > 30:
                    meetingdate = re.search(r'(–|- |-)(.+[0-9]{4})', meetingdate).group(2)
                meetingdate.lstrip()
                if prevdate != meetingdate:  # To acount for duplicates
                    meetingdatetime = "9:30 a.m. on " + meetingdate
                    data = {
                        '_type': 'event',
                        'name': "Electoral Board",
                        'event_description': "",
                        'classification': COMMISSION,
                        'start': self._parse_start(meetingdatetime),
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
                    if "Minutes" in meeting:
                        minuteslink = re.search(r'="(.+)"', meeting).group(1)
                        data["documents"] = self._parse_documents(minuteslink)
                    data['status'] = self._generate_status(data)
                    data['id'] = self._generate_id(data)
                    yield data
                prevdate = meetingdate
            except AttributeError:  # Sometimes meetings will return None
                continue

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

    def _parse_documents(self, link):
        """
        Parse or generate documents.
        """
        return [{'url': "https://app.chicagoelections.com{}".format(link),
                'note': 'Regular Board Meeting Agenda'}]
