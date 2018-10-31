# -*- coding: utf-8 -*-
from datetime import datetime
import re

from city_scrapers.constants import (
    ADVISORY_COMMITTEE, BOARD, COMMITTEE, NOT_CLASSIFIED
)
from city_scrapers.spider import Spider


class IlMetraBoardSpider(Spider):
    name = 'il_metra_board'
    agency_name = 'Illinois Metra'
    timezone = 'America/Chicago'
    allowed_domains = ['metrarail.com']
    start_urls = ['https://metrarr.granicus.com/ViewPublisher.php?view_id=5']
    custom_settings = {'ROBOTSTXT_OBEY': False}

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.listingTable .listingRow'):
            start_time = self._parse_start(item)

            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': '',
                'all_day': False,
                'classification': self._parse_classification(item),
                'start': start_time,
                'end': {
                    'date': start_time['date'],
                    'time': None,
                    'note': '',
                },
                'location': {
                    'neighborhood': 'West Loop',
                    'name': '',
                    'address': '547 West Jackson Boulevard, Chicago, IL',
                },
                'documents': self._parse_documents(item),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, data['name'])
            yield data

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return item.css('td[headers=Name]::text').extract_first().strip()

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        full_name = item.css('td[headers=Name]::text').extract_first()

        if "Metra" in full_name and "Board Meeting" in full_name:
            return BOARD
        elif "Citizens Advisory" in full_name:
            return ADVISORY_COMMITTEE
        elif "Committee Meeting" in full_name:
            return COMMITTEE
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        raw_date_time = item.css('td[headers~=Date]::text').extract_first()
        date_time_str = re.sub(r'\s+', ' ', raw_date_time).strip()

        if not date_time_str:
            return None

        try:
            naive = datetime.strptime(date_time_str, '%b %d, %Y - %I:%M %p')
            return {
                'date': naive.date(),
                'time': naive.time(),
                'note': '',
            }
        except ValueError:
            return None

        return self._naive_datetime_to_tz(naive, 'America/Chicago')

    def _parse_documents(self, item):
        """Parse documents from current and past meetings"""
        documents = []
        agenda_url = item.css('a[href*=Agenda]::attr(href)').extract_first()
        if agenda_url:
            documents.append({
                'url': agenda_url,
                'note': 'Agenda'
            })
        minutes_url = item.css('a[href*=Minutes]::attr(href)').extract_first()
        if minutes_url:
            documents.append({
                'url': minutes_url,
                'note': 'Minutes'
            })
        video_url = item.css(
            'td[headers~=VideoLink] a::attr(onclick)'
        ).extract_first()
        video_url_match = re.search(r'http.*(?=\',\'p)', video_url or '')
        if video_url and video_url_match:
            documents.append({
                'url': video_url_match.group(),
                'note': 'Video'
            })
        return documents
