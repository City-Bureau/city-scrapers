# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
from city_scrapers.constants import COMMISSION
from datetime import time, date
import dateutil.parser

class ChiSsa21Spider(Spider):
    name = 'chi_ssa_21'
    agency_name = 'Lincoln Square Neighborhood Improvement Program'
    timezone = 'America/Chicago'
    allowed_domains = ['www.lincolnsquare.org']
    start_urls = ['http://www.lincolnsquare.org/SSA-no-21-Commission-meetings']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath('//div[@id="content-327081"]/p'):

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

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return 'Commission Meetings'

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        description = 'N/A'

        # The itinerary of the meeting is always stored in the <ul>
        # element immediately following
        detailElement = item.xpath('following-sibling::*[1]')
        name = detailElement.xpath('name()').extract_first()

        if (name == 'ul'):
            topics = list(map(
                lambda topic: ''.join(filter(
                    # Remove any strings that are empty
                    None,
                    [
                        # Title of topic
                        ''.join(topic.xpath('strong/text()').extract()).strip(),
                        # Detail of topic
                        '[' + ''.join(topic.xpath('text()').extract()).strip() + ']'
                    ]
                )),
                detailElement.xpath('li')
            ))

            description = ':'.join(topics)

        return description

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return COMMISSION

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        startTime = self._parse_date(item)
        startTime = startTime.replace(hour=9,minute=0)

        ret = {
            'date': startTime.date(),
            'time': startTime.time(),
            'note': None
        }

        return ret

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        endTime = self._parse_date(item)
        endTime = endTime.replace(hour=11,minute=0)

        ret = {
            'date': endTime.date(),
            'time': endTime.time(),
            'note': 'estimated 2 hours after start time'
        }

        return ret

    def _parse_date(self, item):
        rawDate = item.xpath('strong/text()').extract_first()
        return dateutil.parser.parse(rawDate)

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

        defaultLocation = 'Bistro Campagne, 4518 N. Lincoln Avenue'

        # If location has changed, this is where it is noted
        location = ''.join(
            item.xpath('em//text()').extract()
        ).strip()

        if not location:
            location = defaultLocation

        return {
            'address': location,
            'name': '',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        url = item.xpath('a/@href').extract_first()

        if url:
            return [{'url': url, 'note': 'Meeting notes'}]
        return []

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': '', 'note': ''}]