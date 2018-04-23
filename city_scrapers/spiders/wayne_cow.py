# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider


class Wayne_cowSpider(Spider):
    name = 'wayne_cow'
    long_name = 'Wayne County Committee of the whole'
    allowed_domains = ['www.waynecounty.com']
    start_urls = ['https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.eventspage'):

            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'timezone': self._parse_timezone(item),
                'status': self._parse_status(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
            }

        data['id'] = self._generate_id(data, start_time)

        yield data

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique and in the following format:
        <spider-name>/<start-time-in-YYYYMMddhhmm>/<unique-identifier>/<underscored-event-name>

        Example:
        chi_buildings/201710161230/2176/daley_plaza_italian_exhibit
        """
        return ''

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return 'Committee of the Whole'

    def _parse_description(self, item):
        """
        Event description taken from static text at top of page.
        """
        return ("This committee is a forum for extensive discussion on issues "
                "by the 15 members of the Wayne County Commission. Meetings "
                "are scheduled at the call of the chair of the Commission. "
                "Final approval of items happens at full Commission meetings, "
                "not Committee of the Whole. All Committee of the Whole "
                "meetings are held in the 7th floor meeting room, Guardian "
                "Building, 500 Griswold, Detroit, unless otherwise indicated.")

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'committee-meeting'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        return ''

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return ''

    def _parse_timezone(self, item):
        """
        Parse or generate timzone in tzinfo format.
        """
        return 'America/Detroit'

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self, item):
        """
        Location hardcoded. Text on the URL claims meetings are all held at
        the same location.
        """
        return {
            'url': 'http://guardianbuilding.com/',
            'name': '7th floor meeting room, Guardian Building',
            'address': '500 Griswold St, Detroit, MI 48226',
            'coordinates': {
                'latitude': '',
                'longitude': '',
            },
        }

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

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{
            'url': '',
            'note': '',
        }]
