# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

from city_scrapers.constants import BOARD
from city_scrapers.spider import Spider


class ChiSchoolsSpider(Spider):
    name = 'chi_schools'
    agency_name = 'Chicago Public Schools'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cpsboe.org']
    start_urls = [
        'http://www.cpsboe.org/meetings/planning-calendar',
        'https://www.cpsboe.org/meetings/past-meetings',
    ]

    def parse(self, response):
        event_description = self._parse_description(response)
        for idx, item in enumerate(response.css('#content-primary tr')):
            if idx == 0 and 'calendar' in response.url:
                continue
            if 'calendar' in response.url:
                start = self._parse_start_time(item)
            else:
                start = self._parse_past_start(item)
            if start is not None:
                data = {
                    '_type': 'event',
                    'name': self._parse_name(item, response),
                    'event_description': event_description,
                    'all_day': False,
                    'classification': BOARD,
                    'start': start,
                    'end': {
                        'date': start['date'],
                        'time': None,
                        'note': '',
                    },
                    'documents': self._parse_documents(item, start, response),
                    'location': self._parse_location(item),
                    'sources': self._parse_sources(item, response),
                }
                data['id'] = self._generate_id(data)
                data['status'] = self._generate_status(data, text=event_description)
                yield data

    def _parse_name(self, item, response):
        name = 'Board of Education'
        alt_name = item.css('.mute::text').extract_first()
        if 'past' in response.url and alt_name is not None:
            name = re.sub(r'[\(\)]', '', alt_name)
        return name

    def _parse_description(self, response):
        desc_xpath = '//table/following-sibling::ul//text()|//table/following-sibling::p//text()'
        desc_text = response.xpath(desc_xpath).extract()
        if len(desc_text) == 0:
            return ''
        return ' '.join(desc_text)

    def _remove_line_breaks(self, collection):
        return [x.strip() for x in collection if x.strip() != '']

    def _parse_start_time(self, item):
        raw_strings = item.css('::text').extract()
        date_string_list = self._remove_line_breaks(raw_strings)
        date_string = ''
        if len(date_string_list) > 0:
            date_string = date_string_list[0]
        date_string = date_string.replace(' at', '')
        date_string = date_string.replace(',', "").replace(':', " ")
        try:
            date = datetime.strptime(date_string, '%B %d %Y %I %M %p')
            return {
                'date': date.date(),
                'time': date.time(),
                'note': '',
            }
        except Exception:
            return None

    def _parse_past_start(self, item):
        date_str = item.css('th a::text').extract_first()
        date_obj = datetime.strptime(date_str.strip(), '%B %d, %Y').date()
        return {
            'date': date_obj,
            'time': time(8, 30),
            'note': '',
        }

    def _parse_location(self, item):
        raw_text_list = item.css('::text').extract()
        text_list = self._remove_line_breaks(raw_text_list)[1:]
        text_list = [x for x in text_list if '(' not in x and ')' not in x]
        address = " ".join(text_list)
        return {
            'address': address,
            'name': None,
            'neighborhood': None,
        }

    def _parse_documents(self, item, start, response):
        documents = []
        for doc_link in item.css('td a'):
            doc_url = response.urljoin(doc_link.attrib['href'])
            doc_note = doc_link.css('::text').extract_first()
            if doc_note.lower() == 'proceedings':
                mo_str = start['date'].strftime('%b').lower()
                doc_url = response.urljoin(
                    '/content/documents/{}{dt.day}_{dt.year}proceedings.pdf'.format(
                        mo_str, dt=start['date']
                    )
                )
            documents.append({
                'url': doc_url,
                'note': doc_note,
            })
        return documents

    def _parse_sources(self, item, response):
        """
        Parse sources.
        """
        if 'past' in response.url:
            detail_url = item.css('th a')[0].attrib['href']
            return [{'url': response.urljoin(detail_url), 'note': ''}]
        return [{'url': response.url, 'note': ''}]
