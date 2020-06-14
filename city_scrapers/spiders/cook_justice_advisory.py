'''
NOTES:

* The cook_board_ethics spider uses XPath, but I used python regex

'''

import json
import re
import scrapy
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookJusticeAdvisorySpider(CityScrapersSpider):
    name = 'cook_justice_advisory'
    agency = 'Cook County Justice Advisory'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cookcountyil.gov']

    def start_requests(self):
        # today = datetime.now() # not used anywhere
        url = 'https://www.cookcountyil.gov/service/justice-advisory-council-meetings'
        # url = 'https://www.cookcountyil.gov/calendar-node-field-date/month/{}'.format(mo_str)
        yield scrapy.Request(url=url, method='GET', callback=self.parse)
        

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)
        

    def _parse_event(self, response):
        """Parse the event page."""
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(response),
            classification=ADVISORY_COMMITTEE, 
            start=self._parse_start(response),
            end=self._parse_end(response),
            time_notes='',
            all_day=self._parse_all_day(response),
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting['id'] = self._get_id(meeting)
        meeting['status'] = self._get_status(meeting)
        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all justice advisory council (JAC in calendar) meetings on the page
        """
        relative_event_urls = response.css('div.region-block-2 a::attr(href)').re(r'/event.+') # might have to add .get() at the end?
        return [
            response.urljoin(href)
            for href in relative_event_urls
        ]
        
    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all optional and may e more trouble than they're worth to collect.
        """
        # this method is copied direcly from board ethics spider
        address = response.xpath('//div[@class="field event-location"]/descendant::*/text()'
                                 ).extract()
        for word in ['Location:', ', ', ' ']:
            address.remove(word)
        address = ' '.join(address)
        return {
            'address': address,
            'name': '',
        }
    
    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        # Direcly coped from board ethics spider
        date = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()'
                              ).extract()
        date = ''.join(date).upper()
        return 'ALL DAY' in date

    def _parse_title(self, response):
        """Parse or generate event"""
        # this method is inspired by board ethics spider
        title = response.css('h1::text').extract()
        if "Special" in title:
            return "Special JAC Council Meeting"
        elif "JAC Council Meeting" in title:
            return "JAC Council Meeting"
        else:
            return title

    def _parse_description(self, response):
        """Parse or generate event description."""
        # stuff Leda wrote that is probably insufficient
        #return ' '.join(response.css('div.field-name-field-event-description p::text').extract())

        # copied from board ethics spider
        category_field = response.xpath(
            "//div[contains(., 'Category:') and contains(@class, 'field-label')]"
        )
        field_items = category_field.xpath("./following::div[contains(@class, 'field-items')]")
        return ' '.join(
            field_items.xpath('.//p/text()').extract() +
            field_items.xpath('.//strong/text()').extract()
        ).strip()

    def _parse_start(self, response):
        """Parse start date and time"""
        # copied from board ethics spider
        start = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()'
                               ).extract()
        start = ''.join(start).upper()
        start = start.split(' TO ')[0].strip()
        start = start.replace('(ALL DAY)', '12:00AM')

        return datetime.strptime(start, '%B %d, %Y %I:%M%p')


    def _parse_end(self, response):
        """Parse end date and time"""

        # copied from board ethics spider
        date = response.xpath('//span[@class="date-display-single"]/descendant-or-self::*/text()'
                              ).extract()
        date = ''.join(date).upper()
        date.replace('(ALL DAY)', 'TO 11:59PM')
        start_end = date.split(' TO ')

        if len(start_end) < 2:
            return

        end_time = start_end[1]
        date = start_end[0][:start_end[0].rindex(' ')]
        return datetime.strptime('{} {}'.format(date, end_time), '%B %d, %Y %I:%M%p')

        
    def _parse_links(self, response):
        # not sure what this is supposed to do
        # copied from board ethics spider
        files = response.css('span.file a')
        return [{
            'href': f.xpath('./@href').extract_first(),
            'title': f.xpath('./text()').extract_first()
        } for f in files]
        