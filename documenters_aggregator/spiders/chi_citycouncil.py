# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import requests
import json
import datetime as dt
from pytz import timezone

from documenters_aggregator.spider import Spider


class Chi_citycouncilSpider(Spider):
    name = 'chi_citycouncil'
    long_name = "Chicago City Council"
    ocd_url = 'https://ocd.datamade.us/'
    ocd_tp = 'events/?'
    ocd_d = 'start_date__gt=' + str(dt.date.today()) + '&'
    ocd_srt = 'sort=start_date&'
    ocd_jur = 'jurisdiction=ocd-jurisdiction/'
    ocd_loc = 'country:us/state:il/place:chicago/government'

    allowed_domains = [ocd_url]
    start_urls = [ocd_url + ocd_tp + ocd_d + ocd_srt + ocd_jur + ocd_loc]

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
            parsed_item = self._parse_item(item)
            yield parsed_item

        # self._parse_next(response) yields more (responses to parse
        max_page = data['meta']['max_page']
        page = data['meta']['page']
        while page < max_page:
            yield self._parse_next(response, page)

    def _parse_item(self, item):

        if len(item.get('start_date', None)) > 0:
            start_date = item['start_date'].split('+')[0]
            start_datetime = dt.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
            tz = timezone('America/Chicago')
            start_time = tz.localize(start_datetime).isoformat()
        else:
            start_time = None

        if len(item.get('end_date', '')) > 0:
            end_time = item['end_date'].isoformat()
        else:
            end_time = None

        data = {
            '_type': 'event',
            'id': item['id'],
            'name': item['name'],
            'description': item['description'],
            'classification': 'city council meeting',
            'start_time': start_time,
            'end_time': end_time,
            'all_day': item['all_day'],
            'timezone': 'America/Chicago',
            'status': item['status']
        }
        ocd_response = self._make_ocd_request(data['id'])
        data.update({'location': self._parse_location(ocd_response),
                     'sources': self._parse_sources(ocd_response, data['id'])})
        data['id'] = self._generate_id(data, start_datetime)  # must happen AFTER previous line
        return data

    def _parse_next(self, response, pgnum):
        """
        Get next page.
        """
        pgnum = pgnum + 1
        next_url = self.start_urls[0] + '&page=' + pgnum
        return scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def _make_ocd_request(self, id):
        """
        Makes http request to OCD
        """
        pgurl = self.ocd_url + id + '/'  # Avoid redirect just to add trailing slash
        e_pg = requests.get(pgurl)
        if e_pg.status_code == 200:
            return e_pg.json()
        else:
            return None

    def _parse_location(self, ocd_response):
        """
        Grab location from the event detail page.
        """
        null_location = {
            'url': None,
            'name': None,
            'coordinates': {'longitude': None, 'latitude': None}
        }
        try:
            location = ocd_response.get('location', null_location)
        except:
            location = null_location
        else:
            if not location.get('coordinates', None):
                location['coordinates'] = {'longitude': None, 'latitude': None}
        return location

    def _parse_sources(self, ocd_response, id):
        """
        Grab sources from event detail page.
        """
        pgurl = self.ocd_url + id + '/'
        if ocd_response is None:
            return [{'note': 'ocd-api', 'url': pgurl}]
        else:
            sourcelist = ocd_response['sources']
            sourcelist.append({'note': 'ocd-api', 'url': pgurl})
            sourcelist[0], sourcelist[2] = sourcelist[2], sourcelist[0]
            return sourcelist
