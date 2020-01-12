from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime


class IlAgingAdvisoryCouncilSpider(CityScrapersSpider):
    name = "il_aging_advisory_council"
    agency = "Illinois Aging Advisory Council"
    timezone = "America/Chicago"
    start_urls = [
        "https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx"
    ]
    location = {
        'address': {
            'Springfield': 'One Natural Resources Way #100',
            'Chicago': '160 N. LaSalle Street, 7th Floor'
        },
        'name': {
            'Springfield': 'Illinois Department on Aging',
            'Chicago': 'Michael A. Bilandic Building'
        }
    },

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)

        for item in response.css('div.ms-rtestate-field strong::text').getall():
            try:
                datetime.strptime(item, "%B %d, %Y")
            except ValueError:
                try:
                    datetime.strptime(item[0:12], "%b %d, %Y")
                except ValueError:
                    continue

            meeting = Meeting(
                title='Illinois Department on Aging Advisory Committee Meetings',
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(response),
                location=self.location,
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
        return "Meetings are open to the public"

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

    def _parse_time_notes(self, response):
        """Parse any additional notes on the timing of the meeting"""
        time_notes = response.css('div.ms-rtestate-field p::text').get()
        return time_notes

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _validate_location(self, response):
        location_test = response.css('div.ms-rtestate-field ul li::text').getall()
        if 'One Natural Resources Way, #100' not in location_test[0]:
            raise ValueError("Meeting location has changed")
        elif '7th Floor, 160 N. LaSalle Street' not in location_test[1]:
            raise ValueError("Meeting location has changed")
        else:
            pass

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
