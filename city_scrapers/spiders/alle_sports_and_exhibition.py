# -*- coding: utf-8 -*-
import re
from datetime import timedelta

from dateutil.parser import parse
from lxml import html

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class AlleSportsAndExhibitionSpider(Spider):
    def __init__(self):
        self.startTime = '10:30am'
        self.add = (
            'David L. Lawrence Convention Center , 3rd Floor, '
            '1000 Fort Duquesne Blvd, '
            'Pittsburgh, PA 15222'
        )

    name = 'alle_sports_and_exhibition'
    agency_name = 'Allegheny Sports and Exhibition Authority'
    timezone = 'America/New_York'
    allowed_domains = ['www.pgh-sea.com']
    start_urls = ['http://www.pgh-sea.com/schedule_sea.aspx?yr=2017']

    def _address_time(self, response):
        atext = " ".join(response.xpath('//p//span[@class="ScheduleText"]//text()').extract())
        err_message = 'Look like {name} is changed!!! Please check before procceed!'
        if 'lawrence convention center' not in atext.lower():
            raise (ValueError(err_message.format(name="the address")))

        pattern = r'(\s\d{1,2}\:\d{2}(?:AM|PM|am|pm))'
        atime = re.findall(pattern, atext)

        if len(atime) != 1:
            raise (ValueError(err_message.format(name="the meeting time (10:30am)")))
        else:
            self.startTime = atime[0]

    def _build_datatable(self, response):

        alist_tbody = response.xpath('//table[1]//table[1]//table[1]//td').extract()

        atable = []

        # Remove header and line
        alist_tbody = alist_tbody[4:]
        for i in range(0, len(alist_tbody), 3):
            trees = [html.fragment_fromstring(item) for item in alist_tbody[i:i + 3]]

            texts = [tree.text_content() for tree in trees]
            if 'cancel' in texts[0].lower():
                continue

            urls = [tree.xpath('//a/@href')[0] if tree.xpath('//a/@href') else '' for tree in trees]

            arow = []
            for name, url in zip(texts, urls):
                if url:
                    arow.append({name: url})
                else:
                    arow.append(name)
            atable.append(arow)

        return atable

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        self._address_time(response)

        atable = self._build_datatable(response)

        for row in atable:
            data = {
                '_type': 'event',
                'name': self._parse_name(row),
                'event_description': 'SEA Board Meetings',
                'classification': self._parse_classification(),
                'start': self._parse_start(row),
                'end': self._parse_end(row),
                'all_day': self._parse_all_day(),
                'location': self._parse_location(),
                'documents': self._parse_documents(row),
                'sources': self._parse_sources(),
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            if not data['start']:
                continue
            yield data

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

    def _parse_classification(self):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return BOARD

    def _parse_start_datetime(self, item):
        """
        Parse the start datetime.
        """
        atime = item[0].lower()
        if 'rescheduled' in atime:
            atime = atime.split('(rescheduled)')[1]
        if 'dlcc' in atime:
            atime = atime.split('dlcc')[0]
        if ('am' not in atime or 'pm' not in atime):
            atime = atime + self.startTime
        return parse(atime)

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        datetime_obj = self._parse_start_datetime(item)
        if not datetime_obj:
            return ''
        return {'date': datetime_obj.date(), 'time': datetime_obj.time(), 'note': ''}

    def _parse_end(self, item):
        """
        No end date listed. Estimate 3 hours after start time.
        """
        datetime_obj = self._parse_start_datetime(item)
        if not datetime_obj:
            return ''
        return {
            'date': datetime_obj.date(),
            'time': ((datetime_obj + timedelta(hours=3)).time()),
            'note': 'Estimated 3 hours after start time'
        }

    def _parse_all_day(self):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': self.add,
            'name': 'David L. Lawrence Convention Center',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        documents = []
        if len(item) > 1:
            for adict in item[1:]:
                if isinstance(adict, dict):
                    if 'Meeting Agenda' in adict:
                        documents.append({'note': 'Agenda', 'url': adict['Meeting Agenda']})
                    if 'Minutes of Meeting' in adict:
                        documents.append({'note': 'Minutes', 'url': adict['Minutes of Meeting']})

        return documents

    def _parse_sources(self):
        """"
        Parse or generate sources.
        """
        return [{'url': self.start_urls[0], 'note': ''}]
