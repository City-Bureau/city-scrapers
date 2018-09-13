# -*- coding: utf-8 -*-
import re
from collections import defaultdict
from datetime import datetime, time
from dateutil.parser import parse
from urllib.parse import urljoin

import scrapy

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class DetCityPlanningSpider(Spider):
    name = 'det_city_planning'
    agency_name = 'Detroit City Planning Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    base_url = 'https://www.detroitmi.gov/'
    start_urls = ['https://www.detroitmi.gov/Government/Boards/City-Planning-Commission-Meetings']
    location = {
        'name': 'Committee of the Whole Room, 13th floor, Coleman A. Young Municipal Center',
        'address': '2 Woodward Avenue, Detroit, MI 48226',
        'neighborhood': '',
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        meetings = self._parse_meetings(response)
        for meeting_date_time, document_url in meetings.items():
            data = {
                '_type': 'event',
                'name': 'City Planning Commission Regular Meeting',
                'event_description': '',
                'classification': COMMISSION,
                'start': {'date': meeting_date_time.date(),
                          'time': time(17, 00),
                          'note': 'Meeting runs from 5:00 pm to approximately 8:00 pm'},
                'end': {'date': meeting_date_time.date(), 'time': time(20, 00), 'note': ''},
                'all_day': False,
                'location': self.location,
                'documents': self._create_documents(response.url, document_url),
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_meetings(self, response):
        meetings = self._parse_has_agenda_meetings(response)
        no_agenda_meetings = self._parse_no_agenda_meetings(response)
        for meeting_date in no_agenda_meetings:
            if meeting_date not in meetings:
                meetings[meeting_date] = no_agenda_meetings[meeting_date]
        return meetings

    @staticmethod
    def _parse_no_agenda_meetings(response):
        year_str = datetime.now().year
        meetings = defaultdict(str)
        meetings_text = response.xpath('//tr/td/text()').extract()
        month_day_regex = re.compile("\w+\s\d+")
        for meeting in meetings_text:
            # Check if cell is actual text
            if meeting[0].isalpha():
                month_day = month_day_regex.search(meeting).group(0)
                meeting_date = parse(month_day + ' ' + str(year_str))
                meetings[meeting_date] = ''
        return meetings

    @staticmethod
    def _parse_has_agenda_meetings(response):
        meetings = defaultdict(str)
        date_regex = re.compile("\w+\s\d+,\s\d{4}")
        meeting_agendas = response.xpath('//div[@id="dnn_ctr9526_HtmlModule_lblContent"]//li')
        for agenda in meeting_agendas:
            agenda_link = agenda.xpath('./a/@href').extract_first()
            meeting_date_text = agenda.xpath('./a/text()').extract_first()
            date_text = date_regex.search(meeting_date_text).group(0)
            meeting_date = parse(date_text)
            meetings[meeting_date] = agenda_link
        return meetings

    def _create_documents(self, base_url, url):
        """
        Parse or generate documents.
        """
        if url:
            return [{'url': urljoin(base_url, url), 'note': 'Agenda'}]
        return []
