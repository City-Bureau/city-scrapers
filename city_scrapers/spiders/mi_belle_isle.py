# -*- coding: utf-8 -*-
import re
from datetime import datetime
from dateutil.parser import parse as dateparse
import scrapy
from city_scrapers.spider import Spider


class MiBelleIsleSpider(Spider):
    name = 'mi_belle_isle'
    agency_id = 'Belle Isle Advisory Committee'
    timezone = 'America/Detroit'
    allowed_domains = ['www.michigan.gov']
    start_urls = ["https://www.michigan.gov/dnr/0,4570,7-350-79137_79763_79901---,00.html"]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath('//tbody/tr[child::td/text()]'):
            # Adapted the combined start and end from chi_city_college
            date, start_time, end_time = self._parse_date_and_times(item)
            data = {
                '_type': 'event',
                'name': 'Committee Meeting',
                'event_description': '',
                'classification': 'Committee',
                'start': {
                    'date': date,
                    'time': start_time,
                    'note': '',
                },
                'end': {
                    'date': date,
                    'time': end_time,
                    'note': '',
                },
                'all_day': False,
                'location': self._parse_location(item),
                'documents': self._parse_documents(item),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_date_and_times(self, item):
        """
        Parse start and end date and times.
        """
        date_str = item.xpath('.//td[1]/text()').re(r'[^\*]+')[0]
        time_str = item.xpath('.//td[2]/text()').extract_first().replace('.', '')
        meridian_str = re.findall(r'am|pm', time_str.lower())[0]

        time_start_str = re.findall(r'(\d+?:*?\d*?)(?=\s*-)', time_str)[0]
        time_end_str = re.findall(r'((?<=-)\s*)(\d+?:*?\d*)', time_str)[0][1]

        date_value = dateparse(date_str)
        start_value = dateparse('{0} {1} {2}'.format(date_str, time_start_str, meridian_str))
        end_value = dateparse('{0} {1} {2}'.format(date_str, time_end_str, meridian_str))

        return date_value.date(), start_value.time(), end_value.time()

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        location_name = item.xpath('.//td[3]/text()').extract_first()
        if "flynn" in location_name.lower():
            location_address = "Intersection of Picnic Way and Loiter Way, Belle Isle, Detroit, MI 48207"
        elif "nature zoo" in location_name.lower():
            location_address = "176 Lakeside Drive, Detroit, MI 48207"
        else:
            location_address = "Belle Isle, Detroit, MI 48207"
        return {
            'name': location_name,
            'address': location_address,
            'neighborhood': '',
        }

    # @TODO Get documents from separate list and match up with the date
    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        return [{'url': '', 'note': ''}]
