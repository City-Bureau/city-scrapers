# -*- coding: utf-8 -*-
import re
from dateutil.parser import parse as dateparse
from urllib.parse import urljoin

from city_scrapers.constants import ADVISORY_COMMITTEE
from city_scrapers.spider import Spider


class MiBelleIsleSpider(Spider):
    name = 'mi_belle_isle'
    agency_name = 'Michigan Belle Isle Advisory Committee'
    timezone = 'America/Detroit'
    allowed_domains = ['www.michigan.gov']
    start_urls = [
        (
            'https://www.michigan.gov/dnr/0,4570,7-350-79137'
            '_79763_79901---,00.html'
        )
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath('//tbody/tr[child::td/text()]'):
            # Adapted the combined start and end from chi_city_college
            date, start_time, end_time = self._parse_date_and_times(item)
            data = {
                '_type': 'event',
                'name': 'Committee Meeting',
                'event_description': '',
                'classification': ADVISORY_COMMITTEE,
                'start': {
                    'date': date,
                    'time': start_time,
                    'note': '',
                },
                'end': {
                    'date': date,
                    'time': end_time,
                    'note': '',
                },
                'all_day': False,
                'location': self._parse_location(item),
                'documents': self._match_documents(item, response),
                'sources': [{'url': response.url, 'note': ''}],
            }

            data['status'] = self._generate_status(data, text='')
            data['id'] = self._generate_id(data)

            yield data

    def _parse_date_and_times(self, item):
        """
        Parse start and end date and times.
        """
        date_str = item.xpath('.//td[1]/text()').re(r'[^\*]+')[0]
        time_str = item.xpath(
            './/td[2]/text()'
        ).extract_first().replace('.', '')
        meridian_str = re.findall(r'am|pm', time_str.lower())[0]

        time_start_str = re.findall(r'(\d+?:*?\d*?)(?=\s*-)', time_str)[0]
        time_end_str = re.findall(r'((?<=-)\s*)(\d+?:*?\d*)', time_str)[0][1]

        date_value = dateparse(date_str)
        start_value = dateparse(f'{date_str} {time_start_str} {meridian_str}')
        end_value = dateparse(f'{date_str} {time_end_str} {meridian_str}')

        return date_value.date(), start_value.time(), end_value.time()

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        location_name = item.xpath('.//td[3]/text()').extract_first()
        DEFAULT_LOCATION = {
            'name': 'Belle Isle',
            'address': 'Belle Isle, Detroit, MI 48207',
            'neighborhood': '',
        }
        if location_name is None:
            return DEFAULT_LOCATION
        if "flynn" in location_name.lower():
            location_address = (
                'Intersection of Picnic Way and Loiter Way, '
                'Belle Isle, Detroit, MI 48207'
            )
        elif "nature zoo" in location_name.lower():
            location_address = "176 Lakeside Drive, Detroit, MI 48207"
        else:
            location_address = DEFAULT_LOCATION['address']
        return {
            'name': location_name,
            'address': location_address,
            'neighborhood': '',
        }

    def _parse_documents(self, response):
        """
        Get documents from separate agendas and minutes lists.
        """
        agendas_dict = {}
        minutes_dict = {}
        for agendasItem in response.xpath(
            '//div[contains(@id, "comp_101140")]//a'
        ):
            link_href = agendasItem.xpath('./@href').extract_first()
            link_text = agendasItem.xpath(
                './text()'
            ).extract_first().replace(' (draft)', '')
            agendas_dict[dateparse(link_text).date()] = link_href

        for minutesItem in response.xpath(
            '//div[contains(@id, "comp_101141")]//a'
        ):
            link_href = minutesItem.xpath('./@href').extract_first()
            link_text = minutesItem.xpath(
                './text()'
            ).extract_first().replace(' (draft)', '')
            minutes_dict[dateparse(link_text).date()] = link_href

        return agendas_dict, minutes_dict

    def _match_documents(self, item, response):
        """
        Match up the documents with the date to which they belong
        """
        matched_docs = []
        meeting_date, *_ = self._parse_date_and_times(item)
        meeting_agendas, meeting_minutes = self._parse_documents(response)

        if meeting_date in meeting_agendas:
            agenda_url = meeting_agendas[meeting_date]
            matched_docs.append({
                'url': urljoin(response.url, agenda_url), 'note': 'Agenda'
            })

        if meeting_date in meeting_minutes:
            minutes_url = meeting_minutes[meeting_date]
            matched_docs.append({
                'url': urljoin(response.url, minutes_url), 'note': 'Minutes'
            })

        return matched_docs
