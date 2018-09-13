# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import datetime
import json
from urllib.parse import urljoin, parse_qs

import dateutil.parser
import scrapy

from city_scrapers.constants import CITY_COUNCIL
from city_scrapers.spider import Spider


class ChiCityCouncilSpider(Spider):
    name = 'chi_citycouncil'
    agency_name = 'Chicago City Council'
    timezone = 'America/Chicago'
    allowed_domains = ['ocd.datamade.us']

    endpoint = "https://ocd.datamade.us/events/"
    query = {
        "start_date__gt": str(datetime.date.today()),
        "sort": "start_date",
        "jurisdiction": "ocd-jurisdiction/country:us/state:il/place:chicago/government",
    }
    # the response doesn't include the address for city hall
    address = '121 N LaSalle Dr, Chicago, IL'

    def start_requests(self):
        yield scrapy.FormRequest(url=self.endpoint, method='GET', formdata=self.query, callback=self.parse)

    def parse(self, response):
        """
        This is not a traditional spider, rather, this is a wrapper
        around the Open Civic Data API to which the Chicago City Clerk
        Legistar site info has already been scraped.
        We will attempt to return all events that have been uploaded in the
        future, i.e. past today's date.
        """
        data = json.loads(response.text)
        for url in self._gen_requests(data):
            yield scrapy.Request(url, callback=self._parse_item)

        if self._addtl_pages(data):
            params = parse_qs(response.url)
            params['page'] = self._next_page(data)
            yield scrapy.FormRequest(url=self.endpoint, method='GET', formdata=params, callback=self.parse)

    def _gen_requests(self, data):
        for result in data['results']:
            event_url = urljoin(self.endpoint, '../' + result['id'] + '/')
            yield event_url

    @staticmethod
    def _addtl_pages(data):
        max_page = data['meta']['max_page']
        page = data['meta']['page']
        return max_page > page

    @staticmethod
    def _next_page(data):
        current_page = data['meta']['page']
        return current_page + 1

    def _parse_item(self, response):
        data = json.loads(response.text)
        start = self._parse_time(data.get('start_date', ''))
        end = self._parse_time(data.get('end_date', ''))
        documents = self._parse_documents(data['documents'])
        location = self._parse_location(data)
        item = {
            '_type': 'event',
            'name': data['name'],
            'location': location,
            'id': data['id'],
            'event_description': data['description'],
            'classification': CITY_COUNCIL,
            'start': start,
            'end': end,
            'all_day': data['all_day'],
            'documents': documents,
            'sources': data['sources'],
            'status': data['status']
        }
        end_date = item['end']['date']
        state_date = item['start']['date']
        item['end']['date'] = state_date if end_date is None else end_date
        item['id'] = self._generate_id(item)
        return item

    def _parse_location(self, data):
        return {
            'address': self.address,
            'name': data['location']['name'].strip(),
        }

    def _parse_time(self, timestamp):
        if len(timestamp) <= 0:
            return {'date': None, 'time': None, 'note': ''}

        dt = dateutil.parser.parse(timestamp)
        return {
            'date': dt.date(),
            'time': dt.time(),
            'note': '',
        }

    @staticmethod
    def _parse_documents(documents):
        parsed_documents = []
        for document in documents:
            for link in document['links']:
                parsed_document = {"url": link['url'], 'note': document['note']}
                parsed_documents.append(parsed_document)
        return parsed_documents
