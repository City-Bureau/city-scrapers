# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
from datetime import datetime
from dateutil.parser import parse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class CookElectoralSpider(Spider):
    name = 'cook_electoral'
    agency_name = 'Cook County Electoral Board (Suburban Cook)'
    allowed_domains = ['aba.cookcountyclerk.com']
    start_urls = ['https://aba.cookcountyclerk.com/boardmeetingsearch.aspx']
    download_delay = 1.5

    custom_settings = {
        'COOKIES_ENABLED': True,
        'USER_AGENT': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',
        'USER_AGENT_CACHE_KEY_LENGTH': '256'
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for day in response.css('select#ddlMeetingDate > option ::attr(value)').extract():
            yield scrapy.FormRequest(
                url='https://aba.cookcountyclerk.com/boardmeetingsearch.aspx',
                formdata={
                    'ddlMeetingDate': day,
                    'ddlMeetingYear': str(datetime.now().year),
                    '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
                    '__VIEWSTATEGENERATOR': response.css('input#__VIEWSTATEGENERATOR::attr(value)').extract_first(),
                    '__EVENTVALIDATION': response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__ASYNCPOST': 'true',
                    'ScriptManager1': 'UpdatePanel1|btnGo',
                    'btnGo.x': '29',
                    'btnGo.y': '9'
                },
                callback=self.parse_results,
                errback=self.request_err
            )

    def request_err(self, failure):  # If Request throws an error
        self.logger.error(repr(failure))

    def parse_results(self, item):
        data = {
            '_type': 'event',
            'name': self._parse_name(item),
            'description': self._parse_description(item),
            'classification': BOARD,
            'start': self._parse_start(item),
            'end': self._parse_end(item),
            'timezone': self._parse_timezone(item),
            'status': self._parse_status(item),
            'all_day': self._parse_all_day(item),
            'location': self._parse_location(item),
            'documents': self._parse_documents(item),
            'sources': self._parse_sources(item),
        }

        data['id'] = self._generate_id(data)

        yield data

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique and in the following format:
        <spider-name>/<start-time-in-YYYYMMddhhmm>/<unique-identifier>/<underscored-event-name>

        Example:
        chi_buildings/201710161230/2176/daley_plaza_italian_exhibit
        """
        return ''

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return 'Board Meeting'

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        return ''

    def _parse_start(self, item):
        """
        Parse start date and time.
        """

        datetime = parse(item.css('span#lblMeetingTime ::text').extract_first() + item.css('span#lblDuration ::text').extract_first())

        return  {
            'date': datetime.date(),
            'time': datetime.time()
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return {}

    def _parse_timezone(self, item):
        """
        Parse or generate timzone in tzinfo format.
        """
        return 'America/Chicago'

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'url': '',
            'name': item.css('span#lblLocation ::text').extract_first(),
            'address': item.css('span#lblAddress ::text').extract_first() + ', ' + item.css('span#lblCity ::text').extract_first()
        }

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:
        * cancelled
        * tentative
        * confirmed
        * passed
        By default, return "tentative"
        """
        return 'tentative'

    def _parse_documents(self, item):

        documents = []

        for link in item.css('#currentDocDisplay li a'):
            documents.append({
                'url': link.css('::attr(href)').extract_first(),
                'note': link.css('::text').extract_first()
            })

        return documents

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{
            'url': 'https://www.cookcountyclerk.com/service/board-meetings',
            'note': 'Must submit form to see any dates',
        }]
