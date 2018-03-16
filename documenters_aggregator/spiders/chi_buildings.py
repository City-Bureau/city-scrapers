# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import pytz
import json
import unicodedata
from datetime import datetime

import scrapy
from documenters_aggregator.spider import Spider


class Chi_buildingsSpider(Spider):
    name = 'chi_buildings'
    long_name = 'Public Building Commission of Chicago'
    allowed_domains = ['www.pbcchicago.com']
    base_url = 'http://www.pbcchicago.com/wp-admin/admin-ajax.php?action=eventorganiser-fullcal'
    calendar_date = datetime.now()
    timezone = 'America/Chicago'
    start_urls = ['{}&start={}'.format(
        base_url, calendar_date.strftime('%Y-%m-%d')
    )]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        data = json.loads(response.text)
        for item in data:
            if item.get('category') and 'holiday' not in item['category']:
                start_time = self._naive_datetime_to_tz(self._parse_datetime(item['start']))
                item_data = {
                    '_type': 'event',
                    'id': self._generate_id({'name': item['title']}, start_time),
                    'name': item['title'],
                    'classification': self._parse_classification(item),
                    'start_time': start_time,
                    'end_time': self._naive_datetime_to_tz(self._parse_datetime(item['end'])),
                    'all_day': item['allDay'],
                    'timezone': self.timezone,
                    'status': self._parse_status(item, start_time),
                    'sources': self._parse_sources(item)
                }
                # If it's a board meeting, return description
                if item['category'][0] in ['board-meeting', 'admin-opp-committee-meeting']:
                    yield self._board_meeting(item_data)
                else:
                    # Request each relevant event page, including current data in meta attr
                    req = scrapy.Request(item['url'], callback=self._parse_event, dont_filter=True)
                    req.meta['item'] = item_data
                    yield req

    def _parse_event(self, response):
        """
        Parse event detail page if additional information
        """
        item = {
            'description': self._parse_description(response),
            'location': self._parse_location(response)
        }
        # Merge event details with item data from request meta
        item.update(response.meta.get('item', {}))
        return item

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).

        PBCC has relatively helpful classifications in its WordPress categories.
        """
        return ' '.join([w.capitalize() for w in item['category'][0].split('-')])

    def _parse_status(self, item, start_time):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        tz = pytz.timezone(self.timezone)
        local_cal_date = tz.localize(self.calendar_date)
        if start_time < local_cal_date:
            return 'passed'
        else:
            return 'tentative'

    def _board_meeting(self, item):
        """
        Return a standard location for board meetings
        """
        item_data = {
            'description': None,
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

        Pulling location from WordPress plugin supplied coordinates if available
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

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        description_lines = item.css('.entry-content > p')
        if len(description_lines) == 0:
            return None

        description = ''
        for line in description_lines:
            links = line.css('a')
            if len(links) > 0:
                for link in links:
                    link_text = link.css('*::text').extract_first()
                    if link_text.endswith('.'):
                        link_text = link_text[:-1]
                    description += ' {}: {} '.format(
                        link_text,
                        link.xpath('@href').extract_first()
                    )
            else:
                description += ' '.join([l.extract().strip() for l in line.css('*::text')]) + ' '
        description = unicodedata.normalize('NFKD', description)
        description = description.replace('\n', ' ').strip().replace(' , ', ', ')
        return re.sub(r'\s+', ' ', description)

    def _parse_datetime(self, time_str):
        return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

    def _parse_sources(self, item):
        """
        Parse source from base URL and event link
        """
        return [{'url': item['url']}]
