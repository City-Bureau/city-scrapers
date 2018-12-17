# -*- coding: utf-8 -*-
from datetime import datetime
from lxml import html
from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider
from scrapy.http import FormRequest
from scrapy import Request
import json

class AlleLeagueSpider(Spider):
    custom_settings = {'ROBOTSTXT_OBEY': False}
    name = 'alle_league'
    agency_name = 'Allegheny League of Municipalities'
    timezone = 'America/New_York'
    allowed_domains = ['alleghenyleague.org']
    start_urls = ['http://alleghenyleague.org/calendar-of-events']

    def start_requests(self):
        import pdb;pdb.set_trace()
        url = 'http://alleghenyleague.org/wp-admin/admin-ajax.php'
        payload = {'action': 'simcal_default_calendar_draw_grid',
                   'month': '12',
                   'year': '2018',
                   'id': '417'}
        yield FormRequest(url, formdata=payload)

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        # meeting_titles = response.css('span.simcal-event-title::text').extract()
        # meeting_titles = response.xpath('//span[@class="simcal-event-title"]/text()').extract()
        import pdb;pdb.set_trace()
        data = json.loads(response.body)
        tree=html.fragment_fromstring(adict['data'])
        meeting_titles = tree.xpath('//div//span[@itemprop="name"]//text()')
        startDate = tree.xpath('//div//span[@itemprop="startDate"]//text()')
        endDate = tree.xpath('//div//span[@itemprop="endDate"]//text()')
        # calendar_data = response.xpath('string(//div[@class='
        #                                '"simcal-calendar simcal-default-calendar '
        #                                'simcal-default-calendar-list simcal-default'
        #                                '-calendar-light"]/*)').extract()[0]

        calendar_href = tree.xpath('//div[@class="simcal-event-details simcal-tooltip-content"]//a/@href')
        start_date, end_date = self._prep_date_time(startDate, endDate)
        for index, item in enumerate(meeting_titles):

            data = {
                '_type': 'event',
                'name': item,
                'event_description': item,
                'classification': self._parse_classification(item),
                'start': self._parse_start(start_date[index]),
                'end': self._parse_end(end_date[index]),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'documents': '',
                'sources': self._parse_sources(calendar_href[index]),
            }

            data['status'] = self._generate_status(data,
                                                   item)
            data['id'] = self._generate_id(data)

            yield data

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _prep_date_time(self, startDate, endDate):
        """
        Re-arrage date-time string:
        """
        start_date = []
        end_date = []
        while len(startDate) > 0:
            _start_date = startDate.pop(0)
            if startDate[0].endswith(('pm', 'am')):
                _end_time = endDate.pop(0)
                end_date.append(_start_date+' '+_end_time)
                _start_time = startDate.pop(0)
                _start_date = _start_date + ' ' + _start_time
            else:
                end_date.append(_start_date)

            start_date.append(_start_date)
        return (start_date, end_date)

    def convert_datetime(self, Date):
        """
        Convert datetime string to datetime object.
        """
        if Date.endswith(('pm', 'am')):
            datetime_obj = datetime.strptime(Date,
                                             '%B %d, %Y %I:%M %p')
        else:
            datetime_obj = datetime.strptime(Date,
                                             '%B %d, %Y')
        return datetime_obj

    def _parse_start(self, start):
        """
        Parse start date and time.
        """
        datetime_obj = self.convert_datetime(start)
        return {
            'date': datetime_obj.date(),
            'time': datetime_obj.time(),
            'note': ''
        }

    def _parse_end(self, end):
        """
        Parse end date and time.
        """

        datetime_obj = self.convert_datetime(end)
        return {
            'date': datetime_obj.date(),
            'time': datetime_obj.time(),
            'note': ''
        }

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
            'address': item[-1],
            'name': '',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        return [{'url': '', 'note': ''}]

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': item, 'note': ''}]

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings.
        """
        meeting_description = item
        if ('bod' or 'board') in meeting_description:
            return BOARD
        if 'membership' in meeting_description:
            return COMMITTEE
        return NOT_CLASSIFIED
