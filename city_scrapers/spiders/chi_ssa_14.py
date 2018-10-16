# -*- coding: utf-8 -*-
import re
from datetime import datetime, time

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiSsa14Spider(Spider):
    name = 'chi_ssa_14'
    agency_name = 'Chicago Special Service Area #14 Marquette Park'
    timezone = 'America/Chicago'
    allowed_domains = ['www.mp-security.org']
    start_urls = ['http://www.mp-security.org/public-meetings']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = self._parse_location(response)
        schedule_note = response.css(
            '.col2 span[style]'
        )[0].xpath('*/text()').extract_first()
        year = re.search(r'\d{4}', schedule_note).group()
        # Generate dates for current year's meetings
        meeting_dates = [
            datetime.strptime(f'{year} {meeting.extract()}', '%Y %B %d').date()
            for meeting in response.css('.col2 .announcement strong::text')
        ]

        # Get dates for previous meetings with minutes
        meetings = []
        for item in response.css('.col2 a'):
            link_text = item.extract()
            if not link_text or 'minutes' not in link_text:
                continue
            meetings.append({
                'start': self._parse_start(link_text),
                'documents': self._parse_documents(item),
            })

        # Add any meeting dates that aren't included in the minutes
        for meeting_date in meeting_dates:
            if not any(m['start']['date'] == meeting_date for m in meetings):
                meetings.append({
                    'start': {
                        'date': meeting_date,
                        'time': time(19, 0),
                        'note': '',
                    },
                    'documents': [],
                })

        # Combine results with defaults for events
        for meeting in meetings:
            data = {
                **meeting,
                '_type': 'event',
                'name': 'SSA Governing Commission',
                'event_description': '',
                'classification': COMMISSION,
                'end': {
                    'date': meeting['start']['date'],
                    'time': None,
                    'note': '',
                },
                'all_day': False,
                'location': location,
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_start(self, text):
        """
        Parse start date and time.
        """
        date_match = re.search(r'\w{3,9} \d{1,2}, \d{4}', text)
        month_match = re.search(r'\w{3,9}, \d{4}', text)
        parsed_date = None
        if date_match:
            parsed_date = datetime.strptime(date_match.group(), '%B %d, %Y')
        # Defaults to first of the month if not specified
        elif month_match:
            parsed_date = datetime.strptime(month_match.group(), '%B, %Y')
        if parsed_date:
            return {
                'date': parsed_date.date(),
                'time': time(19, 0),
                'note': '',
            }

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        return {
            'address': ' '.join([
                t.extract() for t in
                response.css('.moduletable-info strong:nth-of-type(1)::text')
            ]).replace('  ', ' '),
            'name': 'Lithuanian Human Services Council',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        return [{
            'url': f'http://www.mp-security.org{item.attrib["href"]}',
            'note': 'Minutes',
        }]
