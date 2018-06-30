# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from city_scrapers.spider import Spider


class Wayne_cowSpider(Spider):
    name = 'wayne_cow'
    agency_id = 'Detroit Committee of the Whole'
    timezone = 'America/Detroit'
    long_name = 'Wayne County Committee of the whole'

    allowed_domains = ['www.waynecounty.com']
    start_urls = ['https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx']

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
                'name': 'Committee of the Whole',
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
        desc_xpath = '//h2[contains(text(), "Committee of the Whole")]/following-sibling::div/section/text()'
        desc = response.xpath(desc_xpath).extract_first()
        return desc

    def _parse_start(self, item):
        """
        Parse start date and time.
        """

        md_str = item.xpath('.//td[2]/text()').extract_first()
        time_str = item.xpath('.//td[3]/text()').extract_first()
        dt_str = '{0}, {1} - {2}'.format(md_str, self.yearStr, time_str)
        try:
            dt = datetime.strptime(dt_str, '%B %d, %Y - %I:%M %p')
        except ValueError:
            return {
                'date': None,
                'time': None,
                'note': '',
            }
        else:
            return {
                'date': dt.date(),
                'time': dt.time(),
                'note': '',
            }

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
