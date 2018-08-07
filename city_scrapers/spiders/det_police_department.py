# -*- coding: utf-8 -*-
import json
import re
from datetime import time

import scrapy
from dateutil.parser import parse

from city_scrapers.spider import Spider


class DetPoliceDepartmentSpider(Spider):
    name = 'det_police_department'
    agency_id = 'Police Department'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['http://www.detroitmi.gov/Government/Detroit-Police-Commissioners-Meetings']
    form_params = {}

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        prev_call_count = response.meta.get('prev_call_count', 0)
        if prev_call_count == 0:
            self.form_params = self._build_form_params(response)
            yield from self._expand_accordian(response, "Meetings")
            # yield from self._expand_accordian(response, "Minutes")
        if prev_call_count > 0:
            post_request_response = self._convert_response(response)
            yield from self._parse_item(post_request_response)

    def _expand_accordian(self, response, text):
        accordian_xpath = '//a[child::div[contains(., "{}")]]/@id'.format(text)
        a_id = response.xpath(accordian_xpath).extract_first()
        yield scrapy.FormRequest.from_response(
            response,
            formname='Form',
            formdata=self.form_params[a_id],
            meta={'prev_call_count': 1},
        )

    def _parse_item(self, post_request_response):
        non_header_rows_xpath = '//tr[position() > 1]'
        rows = post_request_response.xpath(non_header_rows_xpath)
        for row in rows:
            meeting_details = self._parse_meeting_details(row)
            meeting_date_time_text = meeting_details['meeting_date_time']
            meeting_presenter = meeting_details['presenter']
            start = self._parse_date(meeting_date_time_text)
            if start['date'] is None:
                continue
            data = {
                '_type': 'event',
                'name': 'Detroit Police Commissioners Meetings',
                'event_description': meeting_presenter,
                'start': start,
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'sources': [{'url': post_request_response.url, 'note': ''}],
                'documents': [],
                'classification': 'Board'
            }
            data['location'] = self._parse_location(data['start']['time'])
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, meeting_presenter)
            yield data

    @staticmethod
    def _parse_date(meeting_date_time_string):
        try:
            dt = parse(meeting_date_time_string)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': ''}

    @staticmethod
    def _parse_meeting_details(row):
        meeting_table_row = row.xpath("td//text()").extract()
        meeting_details = [s.strip() for s in meeting_table_row if s.strip()]
        if len(meeting_details) == 3:
            *meeting_date_time, presenter = meeting_details
            meeting_date_time = ' '.join(meeting_date_time)
            return {'meeting_date_time': meeting_date_time, 'presenter': presenter}
        if len(meeting_details) == 2:
            meeting_date_time = ' '.join(meeting_details)
            presenter = ''
            return {'meeting_date_time': meeting_date_time, 'presenter': presenter}
        return {'meeting_date_time': '', 'presenter': ''}

    @staticmethod
    def _convert_response(response):
        response_body = response.xpath('//textarea/text()').extract_first()
        html = json.loads(response_body)
        return scrapy.http.TextResponse(url=response.url, body=html['d'], encoding=response.encoding)

    @staticmethod
    def _parse_location(start_time):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        # TODO not sure how to handle this...
        """
         All meetings scheduled for 3:00 pm meet at the Detroit Public Safety Headquarters.
         All meetings scheduled for 6:30 pm are in the community. 
         Community Meetings are subject to change with notice.
        """
        if start_time == time(15, 00):
            return {
                'neigborhood': '',
                'name': 'Detroit Public Safety Headquarters',
                'address': '1301 3rd Ave, Detroit, MI 48226',
            }
        return {
            'neigborhood': '',
            'name': 'Community',
            'address': '',
        }

    def _build_form_params(self, response):
        callbacks = response.xpath('//script[contains(., "ClientCallBackRefdnn")]/text()').extract_first()
        callbacks = callbacks.split('=', 1)[-1]
        params = re.findall(r'dnn.xmlhttp.doCallBack\((.+?)\)', callbacks)
        form_params = {}
        for param in params:
            key, p1, p2 = self._unpack_params(param)
            form_params[key] = {"ctx": "1", "__DNNCAPISCI": p1, "__DNNCAPISCP": p2}
        return form_params

    @staticmethod
    def _unpack_params(params_string):
        """
        helper to parse out params from CDATA tag in script tag
        "'FAQs dnn_ctr7392_FAQs', 1716, GetFaqAnswerSuccess, 'dnn_ctr7392_FAQs_lstFAQs_A2_0', GetFaqAnswerError, null, null, null, 0'"
        """
        p1, p2, _, key, *_ = [p.replace("'", '') for p in params_string.split(',')]
        key = re.sub(r'_A(\d+)_', '_Q\g<1>_', key)
        return key, p1, p2
