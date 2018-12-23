# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

from city_scrapers.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class IlRegionalTransitSpider(Spider):
    name = 'il_regional_transit'
    agency_name = 'Regional Transportation Authority'
    timezone = 'America/Chicago'
    allowed_domains = ['rtachicago.granicus.com']
    start_urls = [
        'http://rtachicago.granicus.com/ViewPublisher.php?view_id=5',
        'http://rtachicago.granicus.com/ViewPublisher.php?view_id=4',
    ]
    custom_settings = {'ROBOTSTXT_OBEY': False}
    location = {
        'name': 'RTA Administrative Offices',
        'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604',
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard http://docs.opencivicdata.org/en/latest/data/event.html
        """
        for item in response.css('.row:not(#search):not(.keywords)'):
            start = self._parse_start(item)
            if start is None:
                continue
            name = self._parse_name(item)
            data = {
                '_type': 'event',
                'name': name,
                'classification': self._parse_classification(name),
                'event_description': '',
                'start': start,
                'end': {
                    'date': start['date'],
                    'time': None,
                    'note': ''
                },
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(item),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }],
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data)
            yield data

    @staticmethod
    def _parse_classification(name):
        name = name.upper()
        if 'CITIZENS ADVISORY' in name:
            return ADVISORY_COMMITTEE
        if 'COMMITTEE' in name:
            return COMMITTEE
        if 'BOARD' in name:
            return BOARD
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_name(item):
        """
        Get event name
        """
        title = item.css('.committee::text').extract_first()
        return title.split(' on ')[0].split(' (')[0]

    @staticmethod
    def _parse_start(item):
        """
        Retrieve the event date, always using 8:30am as the time.
        """
        date_str = ' '.join(item.css('div:first-child::text').extract()).strip()
        date_obj = datetime.strptime(date_str, '%b %d, %Y').date()
        return {
            'date': date_obj,
            'time': time(8, 30),
            'note': 'Initial meetings begin at 8:30am, with other daily meetings following',
        }

    @staticmethod
    def _parse_documents(item):
        documents = []
        for doc_link in item.css('a'):
            if 'onclick' in doc_link.attrib:
                doc_url = re.search(
                    r'(?<=window\.open\(\')http.+(?=\',)', doc_link.attrib['onclick']
                ).group()
            else:
                doc_url = doc_link.attrib['href']
            doc_note = doc_link.css('img::attr(alt)').extract_first()
            # Default to link title if alt text for doc icon isn't available
            if doc_note is None:
                if 'title' in doc_link.attrib:
                    doc_note = doc_link.attrib['title']
                else:
                    continue
            if 'listen' in doc_note.lower():
                doc_note = 'Audio'
            elif 'agenda' in doc_note.lower():
                doc_note = 'Agenda'
            elif 'minutes' in doc_note.lower():
                doc_note = 'Minutes'
            elif 'video' in doc_note.lower():
                doc_note = 'Video'
            documents.append({
                'url': doc_url,
                'note': doc_note,
            })
        return documents
