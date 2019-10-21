import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlProcurementPolicySpider(CityScrapersSpider):
    name = "il_procurement_policy"
    agency = "Illinois Procurement Policy Board"
    timezone = "America/Chicago"
    start_urls = [
        'https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx', 
        'https://www2.illinois.gov/sites/ppb/Pages/board_minutes.aspx'
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".ms-rtestate-field p strong a")[0:]:
            meeting = Meeting(
                title='Procurement Policy Board',
                description='',
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end='',
                all_day='',
                time_notes='End time not specified',
                location = {
                    'name': 'Stratton Office Building',
                    'address': '401 S Spring St, Springfield, IL 62704',
                },
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        time_object = time(10,0)
        date_str = " ".join(item.css("*::text").extract()).strip()
        date_str = re.sub("Agenda.pdf", "", date_str).strip()
        date_object = datetime.strptime(date_str, "%B %d, %Y").date()
        return datetime.combine(date_object, time_object)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return None

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        title_str = " ".join(item.css("*::text").extract()).strip()
        title_str = re.sub("Agenda.pdf", "", title_str).strip()
        title_str += " Agenda"
        links.append({
            'title': title_str,
            'href': response.urljoin(item.attrib['href']),
        })
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url