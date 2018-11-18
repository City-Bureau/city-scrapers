# -*- coding: utf-8 -*-
import os
import unicodedata
from datetime import datetime

from city_scrapers.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers.spider import Spider


class PittAlleghenyLeagueSpider(Spider):
    name = 'pitt_allegheny_league'
    agency_name = 'Allegheny League of Municipalities'
    timezone = 'America/Chicago'
    allowed_domains = ['alleghenyleague.org']
    start_urls = ['http://alleghenyleague.org/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # meeting_titles = response.css('span.simcal-event-title::text').extract()
        # meeting_titles = response.xpath('//span[@class="simcal-event-title"]/text()').extract()
        calendar_data = response.xpath('string(//div[@class='
                                       '"simcal-calendar simcal-default-calendar '
                                       'simcal-default-calendar-list simcal-default'
                                       '-calendar-light"]/*)').extract()[0]

        # Remove \xa0 \xa
        calendar_data = unicodedata.normalize("NFKD", calendar_data)
        # Split events
        calendar_data = calendar_data.split('\n See more details')
        calendar_href = response.xpath('//div[@class="simcal-event-details"]//a/@href').extract()

        for index, item in enumerate(calendar_data):
            item = os.linesep.join([s.replace('\t', '').strip()
                                   for s in item.splitlines()
                                   if s.rstrip()]).split('\n')

            if len(item) < 3:
                continue
            data = {
                '_type': 'event',
                'name': item[1],
                'event_description': item[1],
                'classification': self._parse_classification(item),
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'documents': self._parse_documents(calendar_href[index]),
                'sources': self._parse_sources(calendar_href[index]),
            }

            data['status'] = self._generate_status(data,
                                                   item[-1])
            data['id'] = self._generate_id(data)

            yield data

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        start, _ = item[2].split('-')
        datetime_obj = datetime.strptime(start.strip(),
                                         '%B %d, %Y @ %I:%M %p')
        return {
            'date': datetime_obj.date(),
            'time': datetime_obj.time(),
            'note': ''
        }

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        _, end = item[2].split('-')
        datetime_obj = datetime.strptime(('{date} {time}'
                                          .format(date=item[0], time=end)),
                                         '%B %d, %Y %I:%M %p')
        return {
            'date': datetime_obj.date(),
            'time': datetime_obj.time(),
            'note': ''
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': item[-1],
            'name': '',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        return [{'url': item, 'note': ''}]

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{'url': item, 'note': ''}]

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings.
        """
        meeting_description = item[1].lower()
        if ('bod' or 'board') in meeting_description:
            return BOARD
        if 'membership' in meeting_description:
            return COMMITTEE
        return NOT_CLASSIFIED
