import re
from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse


class MiBelleIsleSpider(CityScrapersSpider):
    name = 'mi_belle_isle'
    agency = 'Michigan Belle Isle Advisory Committee'
    timezone = 'America/Detroit'
    start_urls = ['https://www.michigan.gov/dnr/0,4570,7-350-79137_79763_79901---,00.html']

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath('//tbody/tr'):
            # Adapted the combined start and end from chi_city_college
            start, end = self._parse_start_end(item)
            if not start:
                continue
            meeting = Meeting(
                title='Belle Isle Advisory Committee',
                description='',
                classification=ADVISORY_COMMITTEE,
                start=start,
                end=end,
                time_notes='',
                all_day=False,
                location=self._parse_location(item),
                links=self._match_links(item, start, response),
                source=response.url,
            )

            status_text = ''.join(item.xpath('.//td[3]//text()').extract())
            meeting['status'] = self._get_status(meeting, text=status_text)
            meeting['id'] = self._get_id(meeting)

            yield meeting

    def _parse_start_end(self, item):
        """
        Parse start and end datetimes.
        """
        date_str = re.sub(r'[^a-zA-Z,\d\s]', '', item.css('td:first-child *::text').extract_first())
        time_str = re.sub(
            r'[^a-zA-Z,\d\s:-]', '',
            item.css('td:nth-child(2) *::text').extract_first()
        )
        meridian_str = re.findall(r'am|pm', time_str.lower())[0]

        time_start_str = re.findall(r'(\d+?:*?\d*?)(?=\s*-)', time_str)[0]
        time_end_str = re.findall(r'((?<=-)\s*)(\d+?:*?\d*)', time_str)[0][1]

        try:
            date_value = dateparse(date_str)
        except Exception:
            return None, None
        start_value = dateparse('{} {} {}'.format(date_str, time_start_str, meridian_str))
        end_value = dateparse('{} {} {}'.format(date_str, time_end_str, meridian_str))

        return (
            datetime.combine(date_value.date(), start_value.time()),
            datetime.combine(date_value.date(), end_value.time()),
        )

    def _parse_location(self, item):
        """Parse or generate location."""
        location_name = item.xpath('.//td[3]/text()').extract_first()
        DEFAULT_LOCATION = {
            'name': 'Belle Isle',
            'address': 'Belle Isle, Detroit, MI 48207',
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
        }

    def _parse_links(self, response):
        """Get links for separate agendas and minutes lists."""
        agendas_dict = {}
        minutes_dict = {}
        for agendasItem in response.xpath('//div[contains(@id, "comp_101140")]//a'):
            link_href = agendasItem.xpath('./@href').extract_first()
            link_text = agendasItem.xpath('./text()').extract_first().replace(' (draft)', '')
            link_text = link_text.split(' - ')[0]
            try:
                agendas_dict[dateparse(link_text).date()] = link_href
            except Exception:
                continue

        for minutesItem in response.xpath('//div[contains(@id, "comp_101141")]//a'):
            link_href = minutesItem.xpath('./@href').extract_first()
            link_text = minutesItem.xpath('./text()').extract_first().replace(' (draft)', '')
            try:
                minutes_dict[dateparse(link_text).date()] = link_href
            except Exception:
                continue

        return agendas_dict, minutes_dict

    def _match_links(self, item, start, response):
        """Match up the links with the date to which they belong"""
        matched_links = []
        meeting_date = start.date()
        meeting_agendas, meeting_minutes = self._parse_links(response)

        if meeting_date in meeting_agendas:
            agenda_url = meeting_agendas[meeting_date]
            matched_links.append({'href': urljoin(response.url, agenda_url), 'title': 'Agenda'})

        if meeting_date in meeting_minutes:
            minutes_url = meeting_minutes[meeting_date]
            matched_links.append({'href': urljoin(response.url, minutes_url), 'title': 'Minutes'})

        return matched_links
