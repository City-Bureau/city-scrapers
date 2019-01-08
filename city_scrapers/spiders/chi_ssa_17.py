# -*- coding: utf-8 -*-
from datetime import datetime

from city_scrapers.constants import COMMISSION
from city_scrapers.spider import Spider


class ChiSsa17Spider(Spider):
    name = 'chi_ssa_17'
    agency_name = 'Chicago Special Service Area #17 Lakeview East'
    timezone = 'America/Chicago'
    allowed_domains = ['lakevieweast.com']
    start_urls = ['https://lakevieweast.com/ssa-17/']
    location = {
        'name': 'Lakeview East Chamber of Commerce',
        'address': '3208 N Sheffield Ave Chicago, IL 60657',
        'neighborhood': '',
    }

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        meetings_header = [
            h for h in response.css('.post-content h3') if 'Meeting Dates' in h.extract()
        ][0]
        minutes = self._parse_minutes(response)
        meeting_list = meetings_header.xpath('following-sibling::ul')[0].css('li')

        for item in meeting_list:
            start = self._parse_start(item)
            data = {
                '_type': 'event',
                'name': 'SSA #17 Commission',
                'event_description': '',
                'classification': COMMISSION,
                'start': start,
                'end': {
                    'date': start['date'],
                    'time': None,
                    'note': '',
                },
                'all_day': False,
                'location': self.location,
                'documents': minutes.get(start['date'], []),
                'sources': [{
                    'url': response.url,
                    'note': ''
                }]
            }
            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)
            yield data

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date_str = item.xpath('./text()').extract_first()
        dt = datetime.strptime(
            ', '.join(date_str.split(', ')[-2:]).replace('.', '').strip(),
            '%B %d, %Y at %I:%M %p',
        )
        return {
            'date': dt.date(),
            'time': dt.time(),
            'note': '',
        }

    def _parse_minutes(self, response):
        """Parse minutes from separate list"""
        minutes_header = [
            h for h in response.css('.post-content h3') if 'Meeting Minutes' in h.extract()
        ][0]

        minutes_dict = {}
        minutes_list = minutes_header.xpath('following-sibling::ul')[0].css('a')

        for minutes in minutes_list:
            minutes_text = minutes.xpath('./text()').extract_first()
            minutes_date = datetime.strptime(
                ', '.join(minutes_text.split(', ')[-2:]),
                '%B %d, %Y',
            ).date()
            minutes_dict[minutes_date] = [{'url': minutes.attrib['href'], 'note': 'Minutes'}]

        return minutes_dict
