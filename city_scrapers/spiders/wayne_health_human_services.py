# -*- coding: utf-8 -*-
from datetime import datetime
import re
from dateutil.parser import parse as dateparse
from urllib.parse import urljoin

from city_scrapers.spider import Spider


class Wayne_health_human_servicesSpider(Spider):
    name = 'wayne_health_human_services'
    long_name = 'Wayne County Committee on Health and Human Services'
    agency_id = 'Wayne County Committee on Health and Human Services'
    timezone = 'America/Detroit'
    allowed_domains = ['www.waynecounty.com']
    start_urls = ['https://www.waynecounty.com/elected/commission/health-human-services.aspx']

    # Calendar shows only meetings in current year.
    yearStr = datetime.now().year

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        entries = response.xpath('//tbody/tr')

        for item in entries:
            data = {
                '_type': 'event',
                'name': 'Committee on Health and Human Services',
                'event_description': self._parse_description(item),
                'classification': 'Committee',
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': self._parse_location(),
                'documents': self._parse_documents(item, response.url),
                'sources': [{'url': response.url, 'note': ''}]
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')

            yield data

    @staticmethod
    def _parse_documents(item, base_url):
        url = item.xpath('td/a/@href').extract_first()
        url = urljoin(base_url, url) if url is not None else ''
        if url != '':
            note = item.xpath('td/a/text()').extract_first()
            note = note.lower() if note is not None else ''
            return [{
                'url': url,
                'note': note
            }]
        return []

    @staticmethod
    def _parse_description(response):
        """
        Event description taken from static text at top of page.
        """
        desc_xpath = '//h2[contains(text(), "Health & Human Services")]/following-sibling::div/section/p/text()'
        desc = response.xpath(desc_xpath).extract_first()
        return desc

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Dateparse can't always handle the inconsistent dates, so
        # let's normalize them using scrapy's regular expressions.
        month_str = item.xpath('.//td[2]/text()').re(r'[a-zA-Z]{3}')[0]
        day_str = item.xpath('.//td[2]/text()').re(r'\d+')[0]
        time_str = item.xpath('.//td[3]/text()').extract_first()
        date_str = dateparse('{0} {1} {2} {3}'.format(month_str, day_str, self.yearStr, time_str))

        return self._naive_datetime_to_tz(date_str, source_tz='America/Detroit')

    @staticmethod
    def _parse_location():
        """
        Location hardcoded. Text on the URL claims meetings are all held at
        the same location.
        """
        return {
            'name': '7th floor meeting room, Guardian Building',
            'address': '500 Griswold St, Detroit, MI 48226',
            'neighborhood': '',
        }
