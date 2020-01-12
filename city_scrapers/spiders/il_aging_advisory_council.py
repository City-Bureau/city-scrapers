from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime
import re


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

        self._validate_meeting_times(response)

        valid_date_list = self._create_valid_date_list(response)

        if valid_date_list:
            for item in valid_date_list:
                meeting = Meeting(
                    title='Illinois Department on Aging Advisory Committee Meetings',
                    description='Meetings are open to the public',
                    classification=ADVISORY_COMMITTEE,
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

    def _validate_location(self, response):
        location_test = response.css('div.ms-rtestate-field ul li::text').getall()
        if 'One Natural Resources Way, #100' not in location_test[0]:
            raise ValueError("Meeting location has changed")
        elif '7th Floor, 160 N. LaSalle Street' not in location_test[1]:
            raise ValueError("Meeting location has changed")
        else:
            pass

    def _validate_meeting_times(self, response):
        meeting_time = response.css('div.ms-rtestate-field p::text').get()
        if '1 p.m. - 3 p.m' not in meeting_time:
            raise ValueError("Meeting times have changed")

    def _create_valid_date_list(self, response):

        valid_date_list = []

        initial_list = response.css('div.ms-rtestate-field strong::text').getall()
        for item in initial_list:
            valid_date_match = re.search(r'([A-Z]\w+)\s*(\d\d?),*\s*(\d\d\d\d)', item)
            if valid_date_match:
                month, day, year = valid_date_match.group(1, 2, 3)
                date_item = datetime.strptime(month[0:3] + day + year, '%b%d%Y')
                valid_date_list.append(date_item)

        return valid_date_list

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_time = item.replace(hour=13)
        return start_time

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end_time = item.replace(hour=16)
        return end_time

    def _parse_time_notes(self, response):
        """Parse any additional notes on the timing of the meeting"""
        time_notes = response.css('div.ms-rtestate-field p::text').get()
        return time_notes

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
