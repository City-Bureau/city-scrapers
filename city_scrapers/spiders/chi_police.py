# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import json
from datetime import datetime, date, time
from math import floor

from city_scrapers.spider import Spider


class Chi_policeSpider(Spider):
    name = 'chi_police'
    agency_id = 'Chicago Police Department'
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
        data = json.loads(response.body_as_unicode())

        for item in data:
            # Drop events that aren't Beat meetings or DAC meetings
            name = self._parse_name(item)
            if not name:
                continue

            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'event_description': self._parse_description(name),
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

    def _parse_name(self, item):
        """
        Parse or generate name (e.g. town hall).
        """
        if ('district advisory committee' in item['title'].lower()) or ('DAC' in item['title']):
            return 'District Advisory Committee (DAC)'
        elif 'beat' in item['title'].lower():
            district = self._parse_district(item)
            if district:
                return 'Beat Meeting, District {}'.format(district).strip()
            else:
                return 'Beat Meeting'
        else:
            return None

    def _parse_district(self, item):
        """
        Parse the district number for beat meetings by
        using the biggest number found in the item's title.
        """
        title = [w.replace(',', '').replace('(', '').replace(')', '') for w in item['title'].split()]
        numbers_only = [w for w in title if w.replace('-', '').replace('/', '').isdigit()]
        clean_numbers = [x for w in numbers_only for x in w.split('/')]
        clean_numbers = [x for w in clean_numbers for x in w.split('-')]
        clean_numbers = [int(x) for x in clean_numbers if x]
        if not clean_numbers:
            return None
        else:
            biggest_number = max(clean_numbers)
            district = int(floor(biggest_number / 100))
            return district

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return [{
            'address': item['location'],
            'name': '',
            'neighborhood': ''
        }]

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_description(self, name):
        """
        Parse or generate event description.
        """
        if 'Beat Meeting' in name:
            return ("CPD Beat meetings, held on all 279 police "
                    "beats in the City, provide a regular opportunity "
                    "for police officers, residents, and other community "
                    "stakeholders to exchange information, identify and "
                    "prioritize problems, and begin developing solutions "
                    "to those problems.")
        elif name == 'District Advisory Committee (DAC)':
            return ("Each District Commander has a District Advisory Committee which serves "
                    "to provide advice and community based strategies that address underlying conditions "
                    "contributing to crime and disorder in the district. Each District Advisory Committee "
                    "should represent the broad spectrum of stakeholders in the community including "
                    "residents, businesses, houses of worship, libraries, parks, schools and community-based organizations.")

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        datetime_obj = datetime.strptime(item['start'], "%Y-%m-%dT%H:%M:%S")
        return {
            'start_date': datetime_obj.date(),
            'start_time': datetime_obj.time(),
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
                'end_date': None,
                'end_time': None,
                'note': 'no end time listed'
            }
        else:
            return {
                'end_date': datetime_obj.date(),
                'end_time': datetime_obj.time(),
                'note': ''
            }
    def _parse_sources(self, item):
        """
        Parse sources.
        """
        return [{'url':
                 'https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars',
                 'note': ''}]
