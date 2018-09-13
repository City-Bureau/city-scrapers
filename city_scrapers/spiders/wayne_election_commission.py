# -*- coding: utf-8 -*-
from dateutil.parser import parse
import re
from urllib.parse import urljoin

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class WayneElectionCommissionSpider(Spider):
    name = 'wayne_election_commission'
    agency_name = 'Wayne County Election Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.waynecounty.com']
    start_urls = [
        'https://www.waynecounty.com/elected/clerk/election-commission.aspx'
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {
            'neighborhood': '',
            'name': 'Coleman A. Young Municipal Center, Conference Room 700A',
            'address': '2 Woodward Avenue, Detroit, MI 48226'
        }

        non_empty_rows_xpath = '//tbody/tr[child::td]'
        for item in response.xpath(non_empty_rows_xpath):
            data = {
                '_type': 'event',
                'name': 'Election Commission',
                'event_description': '',
                'classification': COMMISSION,
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': location,
                'documents': self._parse_documents(item, response.url),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    @staticmethod
    def _parse_start(item):
        """
        Parse start date and time.
        """
        note = 'Meeting time are given in the "Notice" document'
        year_xpath = item.xpath(
            'ancestor::table/thead//strong/text()'
        ).extract_first()
        year_regex = re.compile(r'\d{4}')
        year_str = year_regex.findall(year_xpath)[0]
        month_day_str = item.xpath('td[1]//text()').extract_first()
        try:
            meeting_date = parse(month_day_str + ", " + year_str)
            return {'date': meeting_date.date(), 'time': None, 'note': note}
        except ValueError:
            return {'date': None, 'time': None, 'note': note}

    def _parse_documents(self, item, url):
        """
        Parse or generate documents.
        """
        tds = item.xpath('td[position() >1]')
        return [
            self._build_document(td, url) for td in tds
            if self._has_url(td)
        ]

    @staticmethod
    def _has_url(td):
        return td.xpath('.//@href').extract_first()

    @staticmethod
    def _build_document(td, url):
        document_url = urljoin(url, td.xpath('.//@href').extract_first())
        text = td.xpath('.//text()').extract_first()
        return {'url': document_url, 'note': text}
