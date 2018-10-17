# -*- coding: utf-8 -*-
from urllib.parse import urljoin

import scrapy
from dateutil.parser import parse

from city_scrapers.constants import COMMITTEE
from city_scrapers.spider import Spider


class DetCityCouncilSpider(Spider):
    name = 'det_city_council'
    agency_name = 'Detroit City Council'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        months_crawled = response.meta.get('months_crawled', 0)
        if months_crawled < 12:
            yield from self._next_month(response, months_crawled)
        yield from self._generate_requests(response)

    @staticmethod
    def _next_month(response, months_crawled):
        form_params_xpath = "//td[@class='EventNextPrev'][2]/a/@href"
        event_target, event_argument = response.xpath(form_params_xpath).re(r'\'(.*?)\'')
        yield scrapy.FormRequest(
            url=response.url,
            formdata={'__EVENTTARGET': event_target, '__EVENTARGUMENT': event_argument},
            meta={'months_crawled': months_crawled + 1},
        )

    def _generate_requests(self, response):
        anchors = response.xpath("//a[contains(@id, 'ctlEvents')]")
        anchors = [anchor for anchor in anchors if not self._is_recess_event(anchor)]
        for a in anchors:
            yield response.follow(a, self._parse_item)

    @staticmethod
    def _is_recess_event(anchor):
        return 'RECESS' in anchor.xpath('text()').extract_first('').upper()

    def _parse_item(self, response):
        name = self._parse_name(response)
        description = self._parse_description(response)
        start = self._get_date(response, "Start Date")
        end = self._get_date(response, "End Date")
        location = self._get_location(response)
        documents = self._parse_documents(response)

        data = {
            '_type': 'event',
            'name': name,
            'event_description': description,
            'classification': COMMITTEE,
            'start': start,
            'end': end,
            'all_day': False,
            'location': location,
            'documents': documents,
            'sources': [{'url': response.url, 'note': ''}],
        }
        data['id'] = self._generate_id(data)
        data['status'] = self._generate_status(data, text='')
        yield data

    @staticmethod
    def _parse_description(response):
        description_xpath = '//div[span[contains(., "Description")]]/following-sibling::div//p/text()'
        description = response.xpath(description_xpath).extract_first('').strip()
        return description

    @staticmethod
    def _parse_name(response):
        name_xpath = '//span[@class="Head"]/text()'
        name_text = response.xpath(name_xpath).extract_first()
        name_value = name_text.split('-')[0].strip()
        return name_value

    def _get_location(self, response):
        location_xpath = '//div[span[contains(., "Location")]]/following-sibling::div[1]/span/a/text()'
        location_text = response.xpath(location_xpath).extract_first()
        return self._choose_location(location_text)

    @staticmethod
    def _choose_location(location_text):
        # Default to Coleman A. Young Municipal center if no location found
        if not location_text or 'YOUNG MUNICIPAL' in location_text.upper():
            return {
                'neighborhood': '',
                'name': 'Coleman A. Young Municipal Center',
                'address': '2 Woodward Detroit, MI 48226'
            }
        return {'neighborhood': '', 'name': '', 'address': location_text}

    @staticmethod
    def _get_date(response, contains):
        date_xpath = '//div[span[contains(., "{}")]]/following-sibling::div[1]/span[1]/text()'.format(contains)
        date_text = response.xpath(date_xpath).extract_first()
        if date_text:
            dt = parse(date_text)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        return {'date': None, 'time': None, 'note': ''}

    @staticmethod
    def _parse_documents(response):
        documents_selector = '//div[span[contains(., "Description")]]/following-sibling::div//a'
        anchors = response.xpath(documents_selector)
        documents = []
        for a in anchors:
            documents_text = a.xpath('text()').extract_first()
            documents_link = a.xpath('@href').extract_first()
            url = urljoin(response.url, documents_link)
            documents.append({'url': url, 'note': documents_text})
        return documents
