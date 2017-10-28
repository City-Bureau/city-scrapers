## -*- coding: utf-8 -*-

"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

import scrapy
import re
import urllib3

from datetime import datetime
from scrapy import Selector
from scrapy.http import HtmlResponse
from pytz import timezone


class CookcountyilSpider(scrapy.Spider):
	name = 'cookcountyil'
	allowed_domains = ['https://www.cookcountyil.gov']
	start_urls = ['https://www.cookcountyil.gov/calendar']
	domain_root = ['https://www.cookcountyil.gov']

	def parse(self, response):

		"""
		`parse` should always `yield` a dict that follows the `Open Civic Data
		event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`.

		Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
		needs.
		"""

		for item in response.css('div.month-view  a::attr(href)').extract():

			next_url = self.start_urls[-1] + '/' + item
			yield scrapy.Request(item, callback=self.parse_event_page, dont_filter=True)

	def parse_event_page(self, response):
		return{
			'_type':'event',
			'id': self._parse_id(response),
			'name': self._parse_name(response),
			'description': self._parse_description(response),
			'classification': self._parse_classification(response),
			'start_time': self._parse_start_time(response),
			'end_time': self._parse_end_time(response),
			'all_day': self._parse_all_day(response),
			#'_make_date': self._make_date(response),
			'status': self._parse_status(response),
			'location': self._parse_location(response),
			}


	def _parse_id(self, response):

		"""
		Calculate ID.  ID must be unique within the data source being scraped.
		"""
		return response.url.split('/')[-1]


	def _parse_description(self, response):

		"""
		Parse or generate description of meeting.
		"""
		return response.css(".views-field-field-event-description").xpath('.//span/text()').extract()


	def _parse_classification(self, response):

		"""
		Parse or generate classification (e.g. town hall)
		"""
		div = response.xpath("//div")

		for a in div.xpath(".//a/text()"):
			return a.extract()


	def _parse_status(self, response):

		"""
		Parse or generate status of meeting.  Can be:

		*Cancelled
		*Tentative
		*Confirmed
		*Passed

		By default, return "tentative"
		"""
		return ('tentative')

	def _parse_location(self, response):

		"""
		Parse or generate location.  Url, latitude and longitude are optional and
		may be more trouble than they're worth to collect.
		"""
		return{
				'thoroughfare': response.css('.thoroughfare').extract(),
				'premise': response.css('.premise').extract(),
				'locality': response.xpath("//span/text()").extract(),
				'state': response.xpath("//span/text()").extract(),
				'postal-code': response.xpath("//span/text()").extract()
		}

	def _parse_all_day(self, response):

		"""
        Parse or generate all-day status.  Defaults to false only for events that
		have no end time.  Code needs to be incorporated 
        """
		for item in response.css('.date-display-start').extract():

			end_time = self._parse_all_day[-1] + ('/')
			yield scrapy.Request(end_time)



	def _parse_name(self, response):

		"""
		Parse or generate event name.
		"""
		span = response.xpath("//span")

		for a in span.xpath(".//a/text()"):
			return a.extract()


	def _parse_next(self, response):

		"""
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """

		scrapy.Request('"https://www.cookcountyil.gov/calendar-node-field-date/month",  callback=self._parse_next').extract_first()


	def _parse_start_time(self, response):

		"""
        Parse start time for event.
       	"""
		return response.xpath('.//span.date-display-start//text()').extract()


	def _parse_end_time(self, response):

		"""
		Parse end time for event.
		"""
		return response.css('.date-display-single  .date-display-end').extract()


	#def _make_date(self, start_time):

		"""
        Combine year, month, day with variable time and export as timezone-aware,
		ISO-formatted string.

		Not quite sure about how to complete this process...
		"""


		#fmt_string = '{year} {month} {day} {time}{am_pm}'
		#time_string = fmt_string.format(year=year, month=month, day=day, time=time, am_pm=am_pm)

		#naive = datetime.strptime(time_string, '%Y %B %d %I:%M%p')

		#tz = timezone('America/Chicago')

		#return tz.localize(naive).isoformat()
