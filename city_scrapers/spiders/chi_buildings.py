# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import json
import re
from datetime import datetime

import scrapy

from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class ChiBuildingsSpider(Spider):
    name = 'chi_buildings'
    agency_name = 'Public Building Commission of Chicago'
    allowed_domains = ['www.pbcchicago.com']
    base_url = 'http://www.pbcchicago.com/wp-admin/admin-ajax.php?action=eventorganiser-fullcal'
    timezone = 'America/Chicago'
    start_urls = ['{}&start={}'.format(base_url, datetime.now().strftime('%Y-%m-%d'))]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        meeting_types = ['admin-opp-committee-meeting', 'audit-committee', 'board-meeting']

        data = json.loads(response.text)
        for item in data:
            if (item.get('category') != [] and item.get('category')[0] in meeting_types):
                name, dt_time = self._parse_name_time(item['title'])
                start = self._parse_time_dict(self._parse_datetime(item['start']), dt_time)
                end = self._parse_time_dict(self._parse_datetime(item['end']), dt_time)
                end['date'] = start['date']
                if start['time'] == end['time']:
                    end['time'] = None
                item_data = {
                    '_type': 'event',
                    'name': name,
                    'description': item['description'],
                    'classification': self._parse_classification(item.get('category')[0]),
                    'start': start,
                    'end': end,
                    'all_day': False,
                    'timezone': self.timezone,
                    'sources': self._parse_sources(item)
                }
                item_data['status'] = self._generate_status(item_data)
                item_data['id'] = self._generate_id(item_data)

                # If it's a board meeting, return description
                if item['category'][0] in ['board-meeting', 'admin-opp-committee-meeting']:
                    yield self._board_meeting(item_data)
                else:
                    # Request each relevant event page,
                    # including current data in meta attr
                    req = scrapy.Request(
                        item['url'],
                        callback=self._parse_event,
                        dont_filter=True,
                    )
                    req.meta['item'] = item_data
                    yield req

    def _parse_name_time(self, name):
        """Return name with time string removed and time if included"""
        time_match = re.search(r'\d{1,2}:\d{2}([ apm.]{3,5})?', name)
        if not time_match:
            return name, None
        time_str = time_match.group()
        name = name.replace(time_str, '').strip()
        time_str = time_str.strip().replace('.', '')
        # Default to PM if not AM/PM not provided
        if 'm' not in time_str:
            time_str = '{} pm'.format(time_str)
        return name, datetime.strptime(time_str, '%I:%M %p').time()

    def _parse_event(self, response):
        """
        Parse event detail page if additional information
        """
        item = {'location': self._parse_location(response)}
        # Merge event details with item data from request meta
        item.update(response.meta.get('item', {}))
        return item

    def _parse_classification(self, meeting_type):
        """
        Parse or generate classification (e.g. town hall).
        """
        if 'committee' in meeting_type:
            return COMMITTEE
        elif 'board' in meeting_type:
            return BOARD
        return NOT_CLASSIFIED

    def _board_meeting(self, item):
        """
        Return a standard location for board meetings
        """
        item_data = {
            'location': {
                'url': 'https://thedaleycenter.com',
                'name': 'Second Floor Board Room, Richard J. Daley Center',
                'address': '50 W. Washington Street Chicago, IL 60602',
                'coordinates': {
                    'latitude': '41.884089',
                    'longitude': '-87.630191',
                }
            }
        }
        item.update(item_data)
        return item

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        if len(item.css('.eo-event-venue-map')) == 0:
            return {
                'url': None,
                'name': None,
                'coordinates': {
                    'latitude': None,
                    'longitude': None,
                },
            }

        event_script = item.css('script:not([src])')[-1].extract()
        event_search = re.search('var eventorganiser = (.*);', event_script)
        event_details = json.loads(event_search.group(1))
        location = event_details['map'][0]['locations'][0]
        split_tooltip = location['tooltipContent'].split('<br />')
        if '<strong>' in split_tooltip[0]:
            location_name = split_tooltip[0][8:-9]
        else:
            location_name = split_tooltip[0]

        return {
            'url': None,
            'name': location_name,
            'address': split_tooltip[1],
            'coordinates': {
                'latitude': location['lat'],
                'longitude': location['lng'],
            },
        }

    def _parse_time_dict(self, dt, dt_time):
        if dt_time is None:
            dt_time = dt.time()
        return {
            'date': dt.date(),
            'time': dt_time,
            'note': '',
        }

    def _parse_datetime(self, time_str):
        return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

    def _parse_sources(self, item):
        """
        Parse source from base URL and event link
        """
        return [{'url': item['url']}]
