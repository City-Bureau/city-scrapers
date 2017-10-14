# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import requests
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
        item = scrapy.Selector(text=data['content'], type="html")

        for item in response.content['results']:
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item),
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        #pages = response.content('meta')['max_page']
        yield #self._parse_next(response, 1)

    def _parse_next(self, response, pgnum):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        pgnum = pgnum + 1
        next_url = start_urls[0]+'&page='+pgnum  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return item['id']

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return item['classification']

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return item['status']

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        e_pg = requests.get(ocd_url + item.id)
        loc = e_pg.content['location']
        src = e_pg.sources[1]
        return {
            'url': src.url,
            'name': loc.name,
            'coordinates': loc.coordinates,
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return item['all_day']

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item['name']

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return item['description']

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        return item['start_date']

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return item['end_date']
