# -*- coding: utf-8 -*-
import re
import unicodedata

import scrapy
from dateutil.parser import parse

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class DetCharterSchoolBoardsSpider(Spider):
    name = 'det_charter_school_boards'
    agency_name = 'Detroit Public Schools Charter Schools Boards'
    timezone = 'America/Detroit'
    allowed_domains = ['detroitk12.org']
    start_urls = ['http://detroitk12.org/admin/charter_schools/boards/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        yield from self._non_calendar(response)
        yield from self._calendar(response)

    def _non_calendar(self, response):
        items = response.xpath(self._startswith_day_of_week())
        for i, item in enumerate(items):
            start, end = self._parse_start_end_non_calendar(item)
            data = {
                '_type': 'event',
                'name': self._parse_name_non_calendar(item),
                'event_description': self._parse_description_non_calendar(item, i),
                'classification': BOARD,
                'start': start,
                'end': end,
                'all_day': False,
                'location': self._parse_location_non_calendar(item),
                'documents': [],
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _calendar(self, response):
        calendar_events_xpath = "//h2[text()='Calendar of Meetings']/following-sibling::h3"
        items = response.xpath(calendar_events_xpath)
        for item in items:
            end, start = self._parse_start_end_calendar(item)
            location = self._parse_location_calendar(item)
            data = {
                '_type': 'event',
                'name': item.xpath('text()').extract_first('').strip(),
                'event_description': '',
                'classification': BOARD,
                'start': start,
                'end': end,
                'all_day': False,
                'location': location,
                'documents': [],
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    @staticmethod
    def _parse_name_non_calendar(item):
        return item.xpath('.//text()[1]').extract_first()

    def _parse_description_non_calendar(self, item, item_number):
        desc_xpath = self._text_between_dividers(item_number + 1)
        return ' '.join(item.xpath(desc_xpath).extract())

    def _parse_start_end_non_calendar(self, item):
        date_time_text = item.xpath('text()[1]').extract_first()
        date_time_text = self._normalize_date_text(date_time_text)
        date_text, start_time, end_time = self._get_date_time(date_time_text)
        start_dt = parse('{date} {time}'.format(date=date_text, time=start_time), fuzzy=True)
        end_dt = parse('{date} {time}'.format(date=date_text, time=end_time), fuzzy=True)
        start = {'date': start_dt.date(), 'time': start_dt.time(), 'note': ''}
        end = {'date': end_dt.date(), 'time': end_dt.time(), 'note': ''}
        return start, end

    @staticmethod
    def _startswith_day_of_week():
        template = 'starts-with(text(), "{day}")'
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        starts_with_xpath = ' or '.join([template.format(day=day) for day in days])
        return "//p[{starts_with}]".format(starts_with=starts_with_xpath)

    def _text_between_dividers(self, divider_number):
        # Meetings can only be delineated by xpath expression,
        # so use all p tags between nodes of xpath dividers as description.
        # Based on https://stackoverflow.com/questions/10859703/xpath-select-all-elements-between-two-specific-elements
        divider = self._startswith_day_of_week()
        return """{divider}[{k}]
            /following-sibling::p[
                count(.|{divider}[{k_1}]/preceding-sibling::p)
                =
                count({divider}[{k_1}]/preceding-sibling::p)
            ]/text()""".format(divider=divider, k=divider_number, k_1=divider_number + 1)

    @staticmethod
    def _get_date_time(start_text):
        period = re.compile(r'([ap]\.?m\.?)')
        date_text, time_text = start_text.rsplit(',', 1)
        start_time, end_time = time_text.split('-')
        period_1 = period.search(start_time)
        period_2 = period.search(end_time)
        if not period_1:
            start_time = start_time + period_2.group(1)
        return date_text, start_time, end_time

    @staticmethod
    def _normalize_date_text(start_text):
        start_text = unicodedata.normalize('NFKD', start_text).encode('utf-8')
        # mix of em / en dashes convert to single type
        start_text = start_text.replace(b'\xe2\x80\x93', b'-').decode('utf-8')
        return start_text

    @staticmethod
    def _parse_location_non_calendar(item):
        location_details = item.xpath('.//text()[position()>1]').extract()
        location = [l.strip() for l in location_details if l.strip()]
        if len(location) != 3:
            return {'address': ' '.join(location), 'name': '', 'neighborhood': ''}
        return {'name': location[0], 'address': location[1] + ' ' + location[2], 'neighborhood': ''}

    @staticmethod
    def _parse_location_calendar(item):
        address_xpath = './following-sibling::small[1]/span/text()'
        address = item.xpath(address_xpath).extract_first('').strip()
        location = {
            'address': address,
            'name': '',
            'neighborhood': ''
        }
        return location

    @staticmethod
    def _parse_start_end_calendar(item):
        start = item.xpath('./following::small[1]/text()').extract_first()
        date_text, time_text = start.split(' ', 1)
        start_text, end_text = time_text.split('-')
        start_dt = parse('{date} {time}'.format(date=date_text, time=start_text), fuzzy=True)
        start = {'date': start_dt.date(), 'time': start_dt.time(), 'note': ''}
        end_dt = parse('{date} {time}'.format(date=date_text, time=end_text), fuzzy=True)
        end = {'date': end_dt.date(), 'time': end_dt.time(), 'note': ''}
        return end, start
