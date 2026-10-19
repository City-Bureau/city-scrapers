import re
from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa38Spider(CityScrapersSpider):
    name = "chi_ssa_38"
    agency = "Chicago Special Service Area #38 Northcenter"
    timezone = "America/Chicago"
    start_urls = ["http://www.northcenterchamber.com/pages/MeetingsTransparency1"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("div#content-167642 li::text"):
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
        title = "Chamber of Commerce"
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        description = ""
        return description

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_str = item.extract()

        # Use regex to extract parts of the date
        date_words = date_str.split()
        month_name = date_words[0]
        datetime_obj = datetime.strptime(month_name, "%B")
        meeting_day = int(re.findall("[0-9]+", date_words[1])[0])

        # Meeting time defaults to 12:00 AM
        meeting_hour = 0
        # Meeting year defaults to current
        meeting_year = datetime.today().year

        # Handle irregularly formatted parts of date
        for i in range(len(date_words)):
            # Meeting time appears in different formats, but always one
            # index before "a.m." or "p.m."
            if "a.m." in date_words[i]:
                meeting_hour = int(date_words[i - 1])
            elif "p.m." in date_words[i]:
                meeting_hour = int(date_words[i - 1]) + 12

            # Validate reasonable year exists if it starts with "20"
            if date_words[i][0:2] == "20":
                meeting_year = int(re.findall("[0-9]+", date_words[i])[0])

        # Put time, day, and year into datetime object
        start_time = datetime_obj.replace(
            hour=meeting_hour, day=meeting_day, year=meeting_year
        )

        return start_time

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
        # Meetings seemingly ocurred at

        return {
            "address": "4054 N Lincoln Ave, Chicago, IL 60618",
            "name": "Northcenter Chamber of Commerce",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
