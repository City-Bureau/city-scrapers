# -*- coding: utf-8 -*-
import re
from datetime import datetime
from dateutil.parser import parse as dateparse
from urllib.parse import urljoin

import scrapy
from city_scrapers.spider import Spider


class Det_city_planningSpider(Spider):
    name = 'det_city_planning'
    agency_id = 'Detroit City Planning Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    base_url = 'https://www.detroitmi.gov/'
    start_urls = ['https://www.detroitmi.gov/Government/Boards/City-Planning-Commission-Meetings']
    classification = 'Committee'
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
        for item in self._parse_entries(response):

            data = {
                '_type': 'event',
                'name': 'City Planning Commission Regular Meeting',
                'event_description': '',
                'classification': self.classification,
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': ''},
                'all_day': False,
                'location': self.location,
                'documents': self._parse_documents(item),
                'sources': [{'url': response.url, 'note': ''}]
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_entries(self, response):

        # Get all the list items as just the date portion and a link portion
        list_entries = response.xpath('//div[@id="dnn_ctr9526_HtmlModule_lblContent"]//li')

        # Make a big array we will eventually shove everything into
        all_entries_array = []

        # First process the list of dates with agendas
        for list_entry in list_entries:

            # Make each list item into baby array with a date string and a link
            list_entry_link = list_entry.xpath('./a/@href').extract_first()
            list_entry_text = list_entry.xpath('./a/text()').extract_first()

            list_entry_regex = re.compile("\w+\s\d+,\s\d{4}")
            list_entry_text = list_entry_regex.search(list_entry_text).group(0)

            all_entries_array.append([list_entry_text, list_entry_link])

        # print(all_entries_array)

        yearStr = datetime.now().year

        # Now sort through all the entries on the table without agendas

        # We'll compare this array with the above array later
        table_entries_formatted = []

        # Get all of this year's meeting dates (no agendas)
        table_raw = response.xpath('(//tbody)[3]')
        raw_cell_regex = re.compile("\w+\s\d+")

        # Each row has several cells, with a date or garbage
        for table_row_raw in table_raw:
            raw_cells = table_raw.xpath('//tr/td/text()').extract()
            # Examine each cell in each row
            for raw_cell in raw_cells:
                # Check if cell is actual text
                if raw_cell[0].isalpha():
                    # Grab just the date portion of the raw_cell
                    raw_cell = raw_cell_regex.search(raw_cell).group(0)
                    # All raw_cell entries are for the current year, so add it to make a nice date.
                    raw_cell = raw_cell + ', ' + str(yearStr)
                    table_entries_formatted.append(raw_cell)
        print('table entries not shortened')
        print(table_entries_formatted)

        # TODO: Check if there are any repeats or we will get an error

        for entry in all_entries_array:
            if entry[0] in table_entries_formatted:
                table_entries_formatted.remove(entry[0])
        print('table entries formatted list begin')
        print(table_entries_formatted)

        for entry in table_entries_formatted:
            all_entries_array.append([entry, None])

        print('all entries array')
        print(all_entries_array)

        return all_entries_array

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item[0]

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        day_str = item[0]

        # Static time given on the page
        time_str = '5:00 p.m.'
        date_str = dateparse('{0} {1}'.format(day_str, time_str))

        return {'date': date_str.date(), 'time': date_str.time(), 'note': 'Meeting runs from 5:00 pm to approximately 8:00 pm'}

    # def _parse_documents(self, item, allowed_domains):
    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        # return [{'url': item[1], 'note': ''}]
        url = item[1]
        url = urljoin(self.base_url, url) if url is not None else ''
        if url != '':
            # note = item.xpath('td/a/text()').extract_first()
            # note = note.lower() if note is not None else ''
            note = 'Agenda'
            return [{
                'url': url,
                'note': note
            }]
        return []
