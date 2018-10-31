# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import json
from datetime import datetime

from city_scrapers.constants import COMMITTEE, POLICE_BEAT
from city_scrapers.spider import Spider


class ChiPoliceSpider(Spider):
    name = 'chi_police'
    agency_name = 'Chicago Police Department'
    timezone = 'America/Chicago'
    allowed_domains = ['https://home.chicagopolice.org/wp-content/themes/cpd-bootstrap/proxy/miniProxy.php?https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars/district-1/']
    start_urls = ['https://home.chicagopolice.org/wp-content/themes/cpd-bootstrap/proxy/miniProxy.php?https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars/district-1/']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>'
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        try:
            data = json.loads(response.body_as_unicode())
        except json.decoder.JSONDecodeError:
            return

        for item in data:
            # Drop events that aren't Beat meetings or DAC meetings
            classification = self._parse_classification(item)
            if not classification:
                continue

            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(classification, item),
                'event_description': '',
                'classification': classification,
                'all_day': False,
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'location': self._parse_location(item),
                'documents': [],
                'sources': self._parse_sources(item)
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._parse_status(data, item) 
            yield data

    def _parse_status(self, data, item):
        text = item.get('eventDetails', '')
        if text is None:
            text = ''
        return self._generate_status(data, text)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return str(item['calendarId'])

    def _parse_classification(self, item):
        """
        Returns one of the following:
        * District Advisory Committee (DAC)
        * Beat Meeting
        * ''
        """
        if (
            ('district advisory committee' in item['title'].lower())
            or ('DAC' in item['title'])
        ):
            return COMMITTEE
        elif 'beat' in item['title'].lower():
            return POLICE_BEAT
        else:
            return ''

    def _parse_name(self, classification, item):
        """
        Generate a name based on the classfication.
        """
        if classification == COMMITTEE:
            return 'District Advisory Committee'
        elif classification == POLICE_BEAT:
            return 'CAPS District {}, Beat {}'.format(
                item['calendarId'], self._parse_beat(item)
            ).strip()
        else:
            return None

    def _parse_beat(self, item):
        district = str(item['calendarId'])
        beat_split = re.sub(r'[\D]+', ' ', item['title']).split()
        beat_list = []
        for beat_num in beat_split:
            if len(beat_num) > 2 and beat_num.startswith(district):
                beat_list.append(beat_num[len(district):])
            else:
                beat_list.append(beat_num)
        if len(beat_list) == 1:
            return beat_list[0]
        elif len(beat_list) > 1:
            return '{} and {}'.format(', '.join(beat_list[:-1]), beat_list[-1])
        return ''

    def _parse_location(self, item):
        """
        Parses location, adding Chicago, IL to the end of the address
        since it isn't included but can be safely assumed.
        """
        if item['location']:
            address = item['location'] + ' Chicago, IL'
        else:
            address = None
        return {
            'address': address,
            'name': '',
            'neighborhood': ''
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        datetime_obj = datetime.strptime(item['start'], "%Y-%m-%dT%H:%M:%S")
        return {
            'date': datetime_obj.date(),
            'time': datetime_obj.time(),
            'note': ''
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        try:
            datetime_obj = datetime.strptime(item['end'], "%Y-%m-%dT%H:%M:%S")
        except TypeError:
            return {
                'date': None,
                'time': None,
                'note': 'no end time listed'
            }
        else:
            return {
                'date': datetime_obj.date(),
                'time': datetime_obj.time(),
                'note': ''
            }

    def _parse_sources(self, item):
        """
        Parse sources.
        """
        return [{'url':
                 'https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars',
                 'note': ''}]
