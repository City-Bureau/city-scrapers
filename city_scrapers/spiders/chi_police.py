# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import json
from datetime import datetime, date, time
from math import floor

from city_scrapers.constants import COMMITTEE, POLICE_BEAT
from city_scrapers.spider import Spider


class ChiPoliceSpider(Spider):
    name = 'chi_police'
    agency_name = 'Chicago Police Department Beat and District Meetings'
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
            classification = self._parse_classification(item)
            if not classification:
                continue

            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(classification, item),
                'event_description': self._parse_description(classification),
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
        if ('district advisory committee' in item['title'].lower()) or ('DAC' in item['title']):
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
            return classification
        elif classification == POLICE_BEAT:
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

    def _parse_description(self, classification):
        """
        Generate event description based on classification.
        """
        if classification == COMMITTEE:
            return ("Each District Commander has a District Advisory Committee which serves "
                    "to provide advice and community based strategies that address underlying conditions "
                    "contributing to crime and disorder in the district. Each District Advisory Committee "
                    "should represent the broad spectrum of stakeholders in the community including "
                    "residents, businesses, houses of worship, libraries, parks, schools and community-based organizations.")
        else:
            return ("CPD Beat meetings, held on all 279 police "
                    "beats in the City, provide a regular opportunity "
                    "for police officers, residents, and other community "
                    "stakeholders to exchange information, identify and "
                    "prioritize problems, and begin developing solutions "
                    "to those problems.")

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
