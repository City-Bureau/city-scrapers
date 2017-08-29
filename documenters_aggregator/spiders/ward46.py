# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
from datetime import datetime
import pytz


class Ward46Spider(scrapy.Spider):
    name = 'ward46'
    allowed_domains = ['www.james46.org']
    start_urls = ['http://www.james46.org/calendar/list/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.type-tribe_events'):
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item),
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = response.css('.tribe-events-nav-next a ::attr(href)').extract_first()
        print(next_url)
        try:
            return scrapy.Request(next_url, callback=self.parse)
        except TypeError:
            print('No more content')
            return None

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return item.css('.type-tribe_events').re_first("post-[0-9]*")

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        try:
            location = item.css('.tribe-events-venue-details::text').extract_first().strip()
        except ValueError:
            print('Event must be empty')

        return {
            'url': None,
            'name': location,
            'coordinates': {
              'latitude': None,
              'longitude': None,
            },
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        start_time = item.css('.tribe-event-date-start::text').extract_first()

        try:
            datetime.strptime(start_time, "%B %d")
            return True
        except ValueError as v:
            return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        name = item.css('.tribe-event-url')
        name = name.css('a::attr(title)').extract_first()
        return name

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_start(self, item):
        """
        Parse start date and time.
        """

        tz = pytz.timezone('America/Chicago')
        start_time = item.css('.tribe-event-date-start::text').extract_first()

        try:
            start_time = datetime.strptime(start_time, "%B %d @ %I:%M %p").replace(year=datetime.today().year)
            start_time = tz.localize(start_time, is_dst=None)

        except ValueError as e:
            print('Turns out there is a weird format they use with a comma and such')
            try:
                start_time = datetime.strptime(start_time, "%B %d, %Y @ %I:%M %p")
                start_time = tz.localize(start_time, is_dst=None)

            except ValueError:
                print('Likely an all day event. Going to try that formatting next.')

                try:
                    start_time = tz.localize(datetime.strptime(start_time, "%B %d")
                                             .replace(year=datetime.today().year), is_dst=None)
                    return start_time
                except ValueError as v:
                    print(v)
                    return None

        return start_time

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        tz = pytz.timezone('America/Chicago')
        end_time = item.css('.tribe-event-time::text').extract_first()

        try:
            today = datetime.today()
            end_time = tz.localize(datetime.strptime(end_time, "%I:%M %p")
                                   .replace(year=today.year, day=today.day, month=today.month), is_dst=None)
        except TypeError as e:
            print('Probably the end of an all day event, giving us None here')
            return None

        return end_time
