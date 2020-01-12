from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime

class IlAgingAdvisoryCouncilSpider(CityScrapersSpider):
    name = "il_aging_advisory_council"
    agency = "Illinois Aging Advisory Council"
    timezone = "America/Chicago"
    start_urls = ["https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('div.ms-rtestate-field strong::text').getall():
            try:
                datetime.strptime(item, "%B %d, %Y")
            except ValueError:
                try:
                    datetime.strptime(item[0:12], "%b %d, %Y")
                except ValueError:
                    continue

            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Illinois Department on Aging Advisory Committee Meetings"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        try:
            start_time = datetime.strptime(item, "%B %d, %Y")
        except ValueError:
            start_time = datetime.strptime(item[0:12], "%b %d, %Y")  
        return start_time

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "Committee meetings are held from 1 p.m. - 3 p.m. by video conference."

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return { 
            'Springfield': {
                "address": 'One Natural Resources Way #100',  
                "name": "Illinois Department on Aging",
            },
            'Chicago':{
                'address': '160 N. LaSalle Street, 7th Floor',
                'name': 'Michael A. Bilandic Building',
            }
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url



