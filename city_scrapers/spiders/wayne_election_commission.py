# -*- coding: utf-8 -*-
from dateutil.parser import parse
import re
from urllib.parse import urljoin
import scrapy
from city_scrapers.spider import Spider


class WayneElectionCommissionSpider(Spider):
    name = 'wayne_election_commission'
    agency_id = 'Wayne County Election Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.waynecounty.com']
    start_urls = ['https://www.waynecounty.com/elected/clerk/election-commission.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {'neighborhood': '',
                    'name': 'Coleman A. Young Municipal Center, Conference Room 700A',
                    'address': '2 Woodward Avenue, Detroit, MI 48226'}
        meeting_name = 'Election Commission'

        for item in response.xpath('//tbody/tr[child::td]'):

            data = {
                '_type': 'event',
                'name': meeting_name,
                'event_description': '',
                'classification': 'Commission',
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

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        note = 'Meeting time are given in the "Notice" document'
        year_xpath = item.xpath('ancestor::table/thead//strong/text()').extract_first()
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
        documents = [
            {'url': urljoin(url, td.xpath('.//@href').extract_first()),
             'note': td.xpath('.//text()').extract_first()
             } for td in tds if td.xpath('.//@href').extract_first()]
        return documents
