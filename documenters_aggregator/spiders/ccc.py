# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import requests
import json
import datetime as dt


class CccSpider(scrapy.Spider):
    name = 'ccc'
    long_name = "Chicago City Clerk"
    ocd_url = 'https://ocd.datamade.us/'
    ocd_type = 'events/'
    ocd_dfilter = 'start_date__gt='+str(dt.date.today())
    ocd_sort = 'sort=start_date'
    ocd_juris = 'jurisdiction=ocd-jurisdiction/country:us/state:il/place:chicago/government'
    allowed_domains = [ocd_url]
    start_urls = [ocd_url+ocd_type+'?'+ocd_dfilter+'&'+ocd_sort+'&'+ocd_juris]

    def parse(self, response):
        """
        This is not a traditional spider, rather, this is a glorified wrapper
        around the Open Civic Data API to which the Chicago City Clerk
        Legistar site info has already been scraped.
        We will attempt to return all events that have been uploaded in the
        future, i.e. past today's date.
        """
        data = json.loads(response.text)

        for item in data['results']:
            yield {
                '_type': 'event',
                'id': item['id'],
                'name': item['name'],
                'description': item['description'],
                'classification': item['classification'],
                'start_time': item['start_date'],
                'end_time': item['end_date'],
                'all_day': item['all_day'],
                'status': item['status'],
                'location': self._parse_location(item),
            }

        # self._parse_next(response) yields more (responses to parse if necessary.
        max_page = data['meta']['max_page']
        page = data['meta']['page']
        while page <= max_page:
            yield self._parse_next(response, page)

    def _parse_next(self, response, pgnum):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        pgnum = pgnum + 1
        next_url = start_urls[0]+'&page='+pgnum  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """

        e_pg = requests.get(ocd_url + item['id'])
        return e_pg.content['location']
