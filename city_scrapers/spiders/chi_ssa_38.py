# -*- coding: utf-8 -*-
from city_scrapers.spider import Spider
import re

class ChiSsa38Spider(Spider):
    name = 'chi_ssa_38'
    agency_name = 'Chicago Special Service Area #38 Northcenter'
    timezone = 'America/Chicago'
    allowed_domains = ['www.northcenterchamber.com']
    start_urls = ['http://www.northcenterchamber.com/pages/MeetingsTransparency1']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.eventspage'):
            text = response.xpath("//strong").extract()
            meetings = [x for x in text if "href" in x and "Minutes" in x]
            for meeting in meetings:
                data = {
                    '_type': 'event',
                    'name': self._parse_name(item),
                    'event_description': self._parse_description(item),
                    'classification': self._parse_classification(item),
                    'start': self._parse_start(item),
                    'end': self._parse_end(item),
                    'all_day': self._parse_all_day(item),
                    'location': self._parse_location(item),
                    'documents': self._parse_documents(item),
                    'sources': self._parse_sources(item),
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
        return re.search(r'\d{1,2}-\d{1,2}-\d{2,4}', item).group(0)  # Make into datetime

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
            'address': '4054 N. Lincoln Avenue',
            'name': 'Northcenter Chamber of Commerce',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        url = re.search(r'htt.+?">', item).group(0)[:-2]
        return [{'url': url, 'note': 'SSA Commission Meeting Minutes'}]

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': '', 'note': ''}]
