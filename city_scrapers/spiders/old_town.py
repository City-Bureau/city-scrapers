# -*- coding: utf-8 -*-
from datetime import datetime

from city_scrapers.spider import Spider


class OldTownSpider(Spider):
    name = 'old_town'
    agency_name = 'Chicago Special Service Area #48 Old Town'
    timezone = 'America/Chicago'
    allowed_domains = ['oldtownchicago.org']
    start_urls = ['https://oldtownchicago.org/ssa-48']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.meeting-dates-block >h5'):

            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': '',
                'classification': self._parse_classification(item),
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'documents': self._parse_documents(item, response),
                'sources': self._parse_sources(item),
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return 'Regular Commission Meeting'

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'Commission'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        dateStr = item.xpath('text()').extract_first().strip()

        timeChunk = item.xpath('following-sibling::*').extract_first().strip()
        startIndex = timeChunk.index('>')
        endIndex = timeChunk.index('-')
        amPm = timeChunk.index('m')
        dateStr += ' ' + timeChunk[startIndex + 1:endIndex] + timeChunk[amPm - 1:amPm + 1]

        datetimeObject = datetime.strptime(dateStr, '%A %B %d %I:%M%p')
        datetimeObject = datetimeObject.replace(year=datetimeObject.today().year)

        return {
            'date': datetimeObject.date(),
            'time': datetimeObject.time(),
            'note': '',
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        dateStr = item.xpath('text()').extract_first().strip()

        timeChunk = item.xpath('following-sibling::*').extract_first().strip()
        startIndex = timeChunk.index('-')
        amPm = timeChunk.index('m')
        endIndex = amPm - 1
        dateStr += ' ' + timeChunk[startIndex + 1:endIndex] + timeChunk[amPm - 1:amPm + 1]

        datetimeObject = datetime.strptime(dateStr, '%A %B %d %I:%M%p')
        datetimeObject = datetimeObject.replace(year=datetimeObject.today().year)

        return {
            'date': datetimeObject.date(),
            'time': datetimeObject.time(),
            'note': '',
        }

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
            'address': item.xpath('following-sibling::*[1]/text()').extract()[2].strip(),
            'name': item.xpath('following-sibling::*[1]/text()').extract()[1].strip(),
            'neighborhood': '',
        }

    def _parse_documents(self, item, response):
        """
        Parse or generate documents.
        """
        dateStr = item.xpath('text()').extract_first().strip()
        datetimeObject = datetime.strptime(dateStr, '%A %B %d')
        datetimeObject = datetimeObject.replace(year=datetimeObject.today().year)

        for item in response.css('.meeting-minutes-block a.minutes-file'):
            text = item.xpath('text()').extract_first()
            url = item.xpath('@href').extract_first()
            startIndex = text.index('inutes')
            pdfDateStr = text[startIndex + 7:len(text)]
            pdfDatetime = datetime.strptime(pdfDateStr, '%m/%d/%y')
            if (pdfDatetime.date() == datetimeObject.date()):
                return [{'url': url, 'note': 'minutes'}]

        return [{'url': '', 'note': ''}]

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': '', 'note': ''}]
