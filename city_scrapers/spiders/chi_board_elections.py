"""
-I'm able to get the start times for the past meetings. What else should I add?
"""

# -*- coding: utf-8 -*-
from city_scrapers.spider import Spider
from city_scrapers.constants import COMMISSION




class ChiBoardElectionsSpider(Spider):
    name = 'chi_board_elections'
    agency_name = 'Chicago Board of Elections'
    timezone = 'America/Chicago'
    allowed_domains = ['chicagoelections.com']
    start_urls = ['https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        meetings = response.xpath("//a/text()").extract()
        meetingdates = [meeting[22:] for meeting in meetings if "Minutes" not in meeting]

        for meetingdate in meetingdates:
            data = {
                '_type': 'event',
                'name': "Chicago Board of Election Commissioners",
                'event_description': "Meeting",
                'classification': COMMISSION,
                'start': meetingdate,
                'end': {},
                'all_day': False,
                'location': {},
                'documents': {},
                'sources': {},
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

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

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return ''

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        return item.xpath('//div[@class="copy"]/text()').extract()[2]

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return ''

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
            'address': '',
            'name': '',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        return [{'url': '', 'note': ''}]

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': '', 'note': ''}]