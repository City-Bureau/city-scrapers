# -*- coding: utf-8 -*-
from datetime import datetime

from city_scrapers.spider import Spider


class ChiHousingAuthoritySpider(Spider):
    name = 'chi_housing_authority'
    agency_name = 'Chicago Housing Authority'
    timezone = 'America/Chicago'
    allowed_domains = ['www.thecha.org']
    start_urls = ['http://www.thecha.org/doing-business/contracting-opportunities/view-all/Board%20Meeting']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.view-id-solicitations').css("tbody").css("tr"):
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
                'sources': response.url,
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
        name = item.xpath('.//td[2]//text()').extract_first()
        return name

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        description = item.xpath('.//td[3]//text()').extract_first()
        return description

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'Board'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        starttime = item.xpath('.//td[1]//text()').extract_first()
        date = datetime.strptime(starttime, '%b %d, %Y')
        return {
            'date': date.date(),
            'time': '08:30:00',
            'note': '',
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        starttime = item.xpath('.//td[1]//text()').extract_first()
        date = datetime.strptime(starttime, '%b %d, %Y')
        return {
            'date': date.date(),
            'time': '11:00:00',
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
            'address': '4859 S. Wabash, Chicago, IL 60615',
            'name': 'Charles A. Hayes FIC',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        documents = item.css('ul').css('li')
        if len(documents) >= 0:
            return [{
                'url': document.css('.field').css('a').xpath('@href').extract_first(),
                'note': document.css('.field').css('a').xpath('text()').extract_first()
            } for document in documents]
        return []
