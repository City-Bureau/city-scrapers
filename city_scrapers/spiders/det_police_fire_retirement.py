# -*- coding: utf-8 -*-
import scrapy
from dateutil.parser import parse

from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class DetPoliceFireRetirementSpider(Spider):
    name = 'det_police_fire_retirement'
    agency_name = 'Detroit Police and Fire Retirement System'
    timezone = 'America/Detroit'
    allowed_domains = ['www.pfrsdetroit.org']
    start_urls = ['http://www.pfrsdetroit.org/Resources/Meetings']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        yield from self._generate_requests(response)
        yield from self._next_month(response)

    @staticmethod
    def _next_month(response):
        prev_call_count = response.meta.get('prev_call_count', 0)
        if prev_call_count < 12:
            form_params_xpath = "//td[@class='EventNextPrev'][2]/a/@href"
            event_target, event_argument = response.xpath(form_params_xpath).re(r'\'(.*?)\'')
            yield scrapy.FormRequest.from_response(
                response,
                formname='Form',
                formdata={'__EVENTTARGET': event_target, '__EVENTARGUMENT': event_argument},
                meta={'prev_call_count': prev_call_count + 1},
            )

    def _generate_requests(self, response):
        anchor_xpath = '//table[@id="dnn_ctr1010_Events_EventMonth_EventCalendar"]//a[contains(@id, "ctlEvents")]'
        anchors = response.xpath(anchor_xpath)
        for a in anchors:
            yield response.follow(a, self._parse_item)

    def _parse_item(self, response):
        name = self._parse_name(response)
        description = self._parse_description(response)
        start = self._get_date(response, "Start Date")
        end = self._get_date(response, "End Date")
        location = self._get_location(response)
        classification = self._parse_classification(name)

        data = {
            '_type': 'event',
            'name': name,
            'event_description': description,
            'classification': classification,
            'start': start,
            'end': end,
            'all_day': False,
            'location': location,
            'documents': [],
            'sources': [{'url': response.url, 'note': ''}],
        }
        data['id'] = self._generate_id(data)
        data['status'] = self._generate_status(data, text='')
        yield data

    @staticmethod
    def _parse_description(response):
        description_xpath = '//div[span[contains(., "Description")]]/following-sibling::div//p/text()'
        description = response.xpath(description_xpath).extract_first()
        if description is not None:
            return description.strip()
        return ''

    @staticmethod
    def _parse_name(response):
        name_xpath = '//div[@id="dnn_ctr1010_EventDetails_divEventDetails1"]//span[contains(@class, "Head")]/text()'
        name = response.xpath(name_xpath).extract_first()
        return name

    @staticmethod
    def _parse_classification(meeting_name):
        if 'Board' in meeting_name:
            return BOARD
        elif 'Committee' in meeting_name:
            return COMMITTEE
        return NOT_CLASSIFIED

    def _get_location(self, response):
        location_xpath = '//div[contains(@id, "divEventDetailsTemplate3")]//p[contains(., "Address")]/following-sibling::p/text()'
        location_text = response.xpath(location_xpath).extract()
        return self._build_address(location_text)

    @staticmethod
    def _build_address(location_text):
        if len(location_text) > 0:
            *name, address1, address2 = [l.strip() for l in location_text]
            return {
                'name': ', '.join(name),
                'address': address1 + ' ' + address2,
                'neighborhood': '',
            }
        # There are a few recurring board meetings without addresses, but all
        #  meetings seem to take place at this address.
        return {
            'name': '',
            'address': '500 Woodward Avenue, Suite 3000 Detroit, MI 48226',
            'neighborhood': '',
        }

    @staticmethod
    def _get_date(response, contains):
        date_xpath = '//div[span[contains(., "{}")]]/following-sibling::div[1]/span[1]/text()'.format(contains)
        date_text = response.xpath(date_xpath).extract_first()
        if date_text:
            dt = parse(date_text)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        return {'date': None, 'time': None, 'note': ''}
