# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

from datetime import datetime, timedelta
import time as Time

from documenters_aggregator.spider import Spider


class Cook_pubhealthSpider(Spider):
    name = 'cook_pubhealth'
    long_name = 'Cook County Department of Public Health'
    allowed_domains = ['www.cookcountypublichealth.org']
    start_urls = ['http://www.cookcountypublichealth.org/event-registration']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('div[class="event-item"] a::attr(href)').extract():
            next_url = 'http://{0}/{1}'.format(self.allowed_domains[0], item)
            yield scrapy.Request(next_url, callback=self.parse_event_page,
                                 dont_filter=True)  # code doesn't work without this. idk why

    def parse_event_page(self, response):
        times = self._parse_date_time(response)
        data = {
            '_type': 'event',
            'id': self._parse_id(response),
            'name': self._parse_name(response),
            'description': self._parse_description(response),
            'classification': self._parse_classification(response),
            'start_time': times['start'],
            'end_time': times['end'],
            'all_day': self._parse_all_day(response),
            'timezone': 'America/Chicago',
            'status': self._parse_status(response),
            'location': self._parse_location(response),
            'sources': self._parse_sources(response)
        }
        data['id'] = self._generate_id(data, times['start'])
        return data

    def _parse_id(self, response):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return response.url.split('/')[-1]

    def _parse_classification(self, response):
        """
        Parse or generate classification (e.g. town hall).
        """
        name = response.css('td[valign="top"]  h3::text').extract_first()
        if name:
            return name.split(':')[0].strip()
        else:
            return None

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
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': None,
            'address': response.xpath('//input[@type="hidden"][contains(@id, "Location")]/@value').extract_first(),
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date_time_extract = self._extract_date_time(response)
        if 'all day' in date_time_extract:
            return True
        return False

    def _parse_name(self, response):
        """
        Parse or generate event name.
        """
        return response.css('td[valign="top"]  h3::text').extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event name.
        """
        descrip_list = response.css('div[id="tabDesc"] *::text').extract()
        description = ''.join([x.strip() for x in descrip_list])
        return description

    def _extract_date_time(self, response):
        '''
        Extract string with date, start time, end time
        '''
        event_id = response.url.split('/')[-1]
        date_time_extract = response.xpath("//input[@value='{}']/parent::p/text()".format(event_id)).extract()
        if not date_time_extract:
            date_time_extract = response.xpath("//div[contains(@id, 'SingleEvent')]/text()").extract()

        return ''.join([x.strip() for x in date_time_extract])

    def _parse_date_time(self, response):
        """
        Parse start-date-time and end-date-time
        """
        date_time_extract = self._extract_date_time(response)
        if (not date_time_extract) or ('all day' in date_time_extract):
            return {'start': None, 'end': None}

        match = re.search(r'Date:(.+)Time', date_time_extract)
        if not match:
            return {'start': None, 'end': None}
        date = self._clean_date(match.group(1))

        match = re.search(r'Time:(.+)', date_time_extract)
        if not match:
            return {'start': None, 'end': None}
        start_end_time = match.group(1)

        start_end_dict = self._clean_time(start_end_time)
        start = self._make_date(date, start_end_dict['start'])
        end = self._make_date(date, start_end_dict['end'])
        return {'start': start, 'end': end}

    def _clean_time(self, start_end_time):
        '''
        Clean start time and end time
        '''
        start_end_time = ''.join(start_end_time.strip().replace('.', '').upper().split())

        match = re.match(r'(\d+):*(\d*)([APM]*)[-TO–]*(\d*):*(\d*)([APM]*)', start_end_time)
        if not match:
            return {'start': None, 'end': None}
        start_hour, start_min, start_period, end_hour, end_min, end_period = match.groups()
        if not start_min:
            start_min = '00'
        if not end_min:
            end_min = '00'
        if not start_period:
            start_period = end_period

        start = '{hour}:{min}{period}'.format(hour=start_hour, min=start_min, period=start_period)
        end = '{hour}:{min}{period}'.format(hour=end_hour, min=end_min, period=end_period)
        return {'start': start, 'end': end}

    def _clean_date(self, date):
        '''
        If date == 'Today', 'Tomorrow' or a day of the week like 'Friday'
        or 'Last Wednesday', replace it with the date in Mmm dd yyyy format

        If the year is missing, add it on
        '''
        date = date.strip().replace(';', '').replace(',', '')
        today = datetime.today()
        if date == 'Today':
            return today.strftime("%b %d %Y")
        if date == 'Tomorrow':
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%b %d %Y")
        if date.endswith('day'):
            today_wday = today.weekday()
            date_wday = Time.strptime(date.replace('Last ', ''), "%A").tm_wday
            if date.startswith('Last '):
                add_days = (today_wday - date_wday) % 7
            else:
                add_days = (date_wday - today_wday) % 7
            date = today + timedelta(days=add_days)
            return date.strftime("%b %d %Y")
        if len(date) <= 6:
            return '{0} {1}'.format(date, today.year)
        return date

    def _make_date(self, date, time):
        """
        Combine year, month, day with variable time and export as timezone-aware,
        ISO-formatted string.
        """
        time_string = '{0} {1}'.format(date, time)

        try:
            naive = datetime.strptime(time_string, '%b %d %Y %I:%M%p')
        except ValueError:
            return None
        else:
            return self._naive_datetime_to_tz(naive)

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
