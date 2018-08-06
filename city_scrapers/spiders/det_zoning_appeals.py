# -*- coding: utf-8 -*-
from dateutil.parser import parse
from datetime import time
from urllib.parse import urljoin


import scrapy
from city_scrapers.spider import Spider


class DetZoningAppealsSpider(Spider):
    name = 'det_zoning_appeals'
    agency_id = 'Detroit Board of Zoning Appeals'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = ['https://www.detroitmi.gov/Government/Boards/Board-of-Zoning-Appeals-Meeting']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {
            'name': '13th Floor in the Auditorium, Coleman A. Young Municipal Center',
            'address': '2 Woodward Avenue, Detroit, MI 48226',
            'neighborhood': '',
        }
        meeting_name = 'Board of Zoning Appeals'
        classification = 'Board'
        for item in response.xpath('//td[contains(@class, "xl65")]/text()').extract():

            data = {
                '_type': 'event',
                'name': meeting_name,
                'event_description': '',
                'classification': classification,
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': location,
                'documents': self._parse_documents(response, item),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        try:
            meeting_date = parse(item)
            return {'date': meeting_date.date(), 'time': time(9, 00), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': item}

    def _parse_documents(self, response, item):
        """
        Parse or generate documents.
        """
        agendas_xpath = response.xpath('//div[contains(@id, "dnn_ctr7414_HtmlModule_lblContent")]//a')
        meeting_dates = self._parse_start(item)
        for agenda in agendas_xpath:
            agenda_date_text = agenda.xpath('text()').extract_first()
            agenda_date = parse(agenda_date_text)
            agenda_link = agenda.xpath('@href').extract_first()
            if agenda_date.date() == meeting_dates['date']:
                return [{'url': urljoin(response.url, agenda_link), 'note': 'Agenda'}]

        return []
