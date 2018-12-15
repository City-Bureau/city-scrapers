# -*- coding: utf-8 -*-
import unicodedata
from datetime import datetime, timedelta

from dateutil.parser import parse
from lxml import html

from city_scrapers.constants import BOARD, COMMITTEE
from city_scrapers.spider import Spider


class AllePortAuthoritySpider(Spider):
    custom_settings = {'ROBOTSTXT_OBEY': False}
    name = 'alle_port_authority'
    agency_name = 'Port Authority of Allegheny County'
    timezone = 'America/New_York'
    allowed_domains = ['www.portauthority.org']
    start_urls = [
        'https://www.portauthority.org/paac/CompanyInfoProjects/'
        'BoardofDirectors/MeetingAgendasResolutions.aspx'
    ]
    event_year = datetime.now().year

    def _get_address(self, response):
        address = (response.xpath('//table[1]//span/text()').extract()[0])
        return address

    def _build_datatable(self, response):
        alist_tbody = (response.xpath('//table[1]/tbody//td').extract())

        atable = []
        arow = []

        for item in alist_tbody:
            tree = html.fragment_fromstring(item)
            text = tree.text_content()

            url = tree.xpath('//a/@href')
            find_att_b = tree.xpath('//b/text()|//strong/text()')
            if len(find_att_b) >= 1:
                continue
            if url:
                arow.append('{name}: {url}'.format(name=text, url=url[0]))
            else:
                arow.append('{text}'.format(text=unicodedata.normalize("NFKD", text)))
            if len(arow) == 6:
                atable.append(arow)
                arow = []

        return atable

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        address = self._get_address(response)
        atable = self._build_datatable(response)

        for row in atable:
            data = {
                '_type': 'event',
                'name': self._parse_name(row),
                'event_description': '',
                'classification': self._parse_classification(row),
                'start': self._parse_start(row),
                'end': self._parse_end(row),
                'all_day': False,
                'location': self._parse_location(address),
                'documents': self._parse_documents(row),
                'sources': self._parse_sources(row),
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item[0]

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings.
        """
        meeting_title = item[0].lower()
        if 'committee' in meeting_title:
            return COMMITTEE
        return BOARD

    def _parse_start_datetime(self, item):
        """
        Parse the start datetime.
        """
        if 'cancel' in item[2].lower():
            return ''

        if not item[1].strip():
            if 'stakeholder' in item[0].lower():
                time = '8:30 a.m.'
            if 'performance oversight' in item[0].lower():
                time = '9:00 a.m.'
            else:
                time = '9:30 a.m.'
        else:
            time = item[1]
        date = ('{year} {date}'.format(year=self.event_year, date=item[2]))

        time_string = '{0} {1}'.format(date, time)
        return (parse(time_string))

    def _parse_start(self, item):
        datetime_obj = self._parse_start_datetime(item)
        if not datetime_obj:
            return ''
        return {'date': datetime_obj.date(), 'time': datetime_obj.time(), 'note': ''}

    def _parse_end(self, item):
        """
        No end date listed. Estimate 3 hours after start time.
        """
        datetime_obj = self._parse_start_datetime(item)
        if not datetime_obj:
            return ''
        return {
            'date': datetime_obj.date(),
            'time': ((datetime_obj + timedelta(hours=3)).time()),
            'note': 'Estimated 3 hours after start time'
        }

    def _parse_location(self, address):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        room = 'Neal H. Holmes Board Room'
        street = '345 Sixth Avenue, Fifth Floor'
        city = 'Pittsburgh, PA 15222-2527'

        if room in address and street in address:
            return {
                'address': ('{room}, {street}, {city}'.format(room=room, street=street, city=city)),
                'name': '',
                'neighborhood': '',
            }

        else:
            raise (ValueError('Look like the address is changed!! Please fix it!!!'))

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        documents = []
        details = item[5]
        if details.startswith('Minutes: http'):
            documents.append({'note': 'Minutes', 'url': details.split(' ')[-1]})

        agenda = item[3]
        if agenda.startswith('Agenda: http'):
            documents.append({'note': 'Agenda', 'url': agenda.split(' ')[-1]})

        resolution = item[4]
        if resolution.startswith('Resolutions: http'):
            documents.append({'note': 'Resolution', 'url': resolution.split(' ')[-1]})

        return documents

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': self.start_urls[0], 'note': ''}]
