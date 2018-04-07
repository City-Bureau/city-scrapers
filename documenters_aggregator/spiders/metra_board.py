# -*- coding: utf-8 -*-
from datetime import datetime
import re

from documenters_aggregator.spider import Spider


class Metra_boardSpider(Spider):
    name = 'metra_board'
    long_name = 'Metra Board of Directors'
    allowed_domains = ['metrarail.com']
    start_urls = ['https://metrarr.granicus.com/ViewPublisher.php?view_id=5']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.listingTable')[0].css('.listingRow'):
            start_time = self._parse_start(item)

            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'description': '',
                'classification': self._parse_classification(item),
                'start_time': start_time,
                'end_time': None,
                'timezone': 'America/Chicago',
                'all_day': False,
                'location': self._parse_location(item),
                'sources': self._parse_sources(response),
            }

            data['id'] = self._generate_id(data, start_time)
            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item.css('td[headers=Name]::text').extract_first()

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return ''

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'transit'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        raw_date_time = item.css('td[headers=Date]::text').extract_first()
        date_time_str = re.sub(r'\s+', ' ', raw_date_time).strip()

        if not date_time_str:
            return None

        try:
            naive = datetime.strptime(date_time_str, '%b %d, %Y - %I:%M %p')
        except ValueError:
            return None

        return self._naive_datetime_to_tz(naive, 'America/Chicago')

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return ''

    def _parse_timezone(self, item):
        """
        Parse or generate timzone in tzinfo format.
        """
        return 'America/Chicago'

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
            'url': '',
            'name': '',
            'address': '547 West Jackson Boulevard, Chicago, IL',
            'coordinates': {
                'latitude': '',
                'longitude': '',
            },
        }

    def _parse_sources(self, response):
        """
        Parse or generate sources.
        """
        return [{
            'url': response.url,
            'note': '',
        }]
