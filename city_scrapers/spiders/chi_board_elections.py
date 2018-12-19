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
        text = response.xpath('//text()').extract()
        # Will return full dates, like "9:30 a.m. on Dec. 11, 2018"
        dates = [
            re.search(r'\d{1,2}:.*20\d{2}', x).group(0)
            for x in text
            if re.search(r'\d{1,2}:.*20\d{2}', x)
        ]
        # Has meeting location
        next_meeting = response.xpath('//div[@class="copy"]/text()').extract()
        for date in dates:
            date.replace('\xa0', ' ')
            data = {
                '_type': 'event',
                'name': "Electoral Board",
                'event_description': "",
                'classification': COMMISSION,
                'start': self._parse_start(date, ""),
                'all_day': False,
                'documents': self._parse_documents(response, None),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }],
            }
            if any("69" in x for x in next_meeting):
                data['location'] = self._parse_location(response)
            else:
                raise ValueError("The address has changed.")

            data['end'] = {
                'date': data['start']['date'],
                'time': None,
                'note': '',
            }
            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _prev_meetings(self, response):
        """
        Meetingdate regex first searches for the 3 types of hyphens that chi_board_elections
        uses (they like switching it up), and then finds a year number,
        and returns everything in between.
        """

        meetings = response.xpath("//a|//span/text()").extract()
        prevdate = None
        for meeting in meetings:
            meeting.replace('\xa0', ' ')  # Gets rid of non-breaking space character
            try:
                meetingdate = re.search(r'(–|- |-)(.+[0-9]{4})', meeting).group(2)
                while len(meetingdate) > 30:
                    meetingdate = re.search(r'(–|- |-)(.+[0-9]{4})', meetingdate).group(2)
                meetingdate.lstrip()
                if prevdate != meetingdate:  # To acount for duplicates
                    data = {
                        '_type': 'event',
                        'name': "Electoral Board",
                        'event_description': "",
                        'classification': COMMISSION,
                        'start': self._parse_start(meetingdate, meeting),
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
                    # Checks for link, will catch minutes or video links for one date
                    if "href" in meeting:
                        data["documents"].append(self._parse_documents(response, meeting))
                    nextindex = meetings.index(meeting) + 1
                    # In case there's both minutes and video for one date
                    if nextindex < len(meetings):
                        nextmeeting = meetings[nextindex]
                        if meetingdate and "href" in nextmeeting:
                            data["documents"].append(self._parse_documents(response, nextmeeting))
                    data['status'] = self._generate_status(data)
                    data['id'] = self._generate_id(data)
                    yield data
                if not self._different_time(meeting):  # To handle the odd 7 AM/7PM meetings
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

    def _parse_start(self, meetingdate, meeting):
        """
        Parse start date and time.
        """
        meetingtime = "9:30 AM on "
        if "7 " in meeting:
            time = re.search(r'7.+\S[m,.]', meeting).group(0)
            str(time)
            time = time.replace("7 ", "7:00 ")
            meetingtime = "{} on ".format(time)

        if ":" not in meetingdate or meeting:
            meetingdate = meetingtime + meetingdate
        formatitem = meetingdate.replace("a.m.", "AM")
        formatitem = formatitem.replace("am", "AM")
        formatitem = formatitem.replace("p.m.", "PM")
        formatitem = formatitem.replace("Sept", "Sep")
        try:
            datetime_item = datetime.strptime(formatitem, '%I:%M %p on %b. %d, %Y')
        except ValueError:  # Some months are abbreviated, some are not
            datetime_item = datetime.strptime(formatitem, '%I:%M %p on %B %d, %Y')
        dicti = {'date': datetime_item.date(), 'time': datetime_item.time(), 'note': ''}
        return dicti

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

    def _parse_documents(self, response, meeting):
        """
        Parse or generate documents.
        """
        if "minutes" in response.url:
            if "Minutes" in meeting:
                minuteslink = re.search(r'"\/.+"', meeting).group(0).strip('"')
                return {
                    'url': "https://app.chicagoelections.com{}".format(minuteslink),
                    'note': 'Regular Board Meeting Agenda'
                }
            elif "youtu" in meeting:
                videolink = re.search(r'"h.+"', meeting).group(0).strip('"')
                return {'url': videolink, 'note': "Regular Board Meeting Video"}
        else:
            link = response.xpath("//a/@href").extract()[2]
            return [{
                'url': "https://app.chicagoelections.com{}".format(link),
                'note': 'Regular Board Meeting Agenda'
            }]

    def _different_time(self, meeting):
        """
        Checks if the meeting is an AM meeting, in which case there would
        be a 7 a.m. and 7 p.m. meeting on the same day, so we flag the bot to run again.
        """
        time = re.search(r'7 [ap]', meeting)
        return True if time else False
