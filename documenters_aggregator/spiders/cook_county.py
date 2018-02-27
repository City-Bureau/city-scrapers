# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime
from pytz import timezone

from documenters_aggregator.spider import Spider


class Cook_countySpider(Spider):
    name = 'cook_county'
    long_name = 'Cook County Government'
    allowed_domains = ['www.cookcountyil.gov']
    start_urls = ['https://www.cookcountyil.gov/calendar?page=0']
    event_timezone = 'America/Chicago'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        for url in self._get_event_urls(response):
            next_url = 'https://{0}{1}'.format(self.allowed_domains[0], url)
            yield scrapy.Request(next_url, callback=self._parse_event, dont_filter=True)

        next_url = self._parse_next(response)
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def _parse_event(self, response):
        """
        Parse the event page.
        """
        start_time_object = self._parse_start(response)
        data = {
            '_type': 'event',
            'name': self._parse_name(response),
            'description': self._parse_description(response),
            'classification': self._parse_classification(response),
            'start_time': timezone(self.event_timezone).localize(start_time_object),
            'end_time': self._parse_end(response),
            'all_day': self._parse_all_day(response),
            'timezone': self.event_timezone,
            'status': self._parse_status(response),
            'location': self._parse_location(response),
            'sources': self._parse_sources(response)
        }
        data['id'] = self._generate_id(data, start_time_object)
        return data

    def _get_event_urls(self, response):
        """
        Get urls for all events on the page.
        """
        event_urls = response.xpath('//div[@class="view-content"]//a/@href').extract()
        return list(set([x for x in event_urls if '/event/' in x and 'cancelled' not in x]))

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        split_url = response.url.split('page=')
        next_number = int(split_url[1]) + 1
        if next_number <= 11:
            return '{0}page={1}'.format(split_url[0], next_number)
        else:
            return None

    def _parse_classification(self, response):
        """
        Parse or generate classification (e.g. town hall).
        """
        category = response.xpath('//div[@class="field event-categories"]/descendant-or-self::*/text()').extract()
        category = ''.join(category).replace('Category:', '').strip()
        if not category:
            return 'Not classified'
        else:
            return category

    def _parse_status(self, response):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        address = response.xpath('//div[@class="field event-location"]/descendant::*/text()').extract()
        address = ' '.join([x.strip() for x in address])
        address = address.replace('Location:', '').strip()
        return {
            'url': None,
            'address': address,
            'name': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()').extract()
        date = ''.join(date).upper()
        return 'ALL DAY' in date

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        return response.xpath('//h1/text()').extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event description.
        """
        description = response.xpath('//div[@class="content"]/div[contains(@class, "field-name-field-event-")]/descendant-or-self::*')
        descrip_str = ''
        for d in description:
            descrip_str = ' '.join([descrip_str, ' '.join(d.xpath('text()').extract())])
            descrip_str = ' '.join([descrip_str, ' '.join(d.xpath('a/@href').extract())])
        return descrip_str.strip()

    def _parse_start(self, response):
        """
        Parse start date and time.
        """
        start = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()').extract()
        start = ''.join(start).upper()
        start = start.split(' TO ')[0].strip()
        start = start.replace('(ALL DAY)', '12:00AM')

        return datetime.strptime(start, '%B %d, %Y %I:%M%p')

    def _parse_end(self, response):
        """
        Parse end date and time.
        """
        date = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()').extract()
        date = ''.join(date).upper()
        date.replace('(ALL DAY)', 'TO 11:59PM')
        start_end = date.split(' TO ')

        if len(start_end) < 2:
            return None

        end_time = start_end[1]
        date = start_end[0][:start_end[0].rindex(' ')]
        end = '{0} {1}'.format(date, end_time)
        naive = datetime.strptime(end, '%B %d, %Y %I:%M%p')
        tz = timezone(self.event_timezone)
        return tz.localize(naive)

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
