import re
from datetime import datetime

import pytz
from city_scrapers_core.constants import BOARD, COMMITTEE, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class DetBoardOfEducationSpider(CityScrapersSpider):
    name = "det_board_of_education"
    agency = "Detroit Public Schools Community District"
    timezone = "America/Detroit"
    start_urls = ["https://www.detroitk12.org/site/handlers/icalfeed.ashx?MIID=14864"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.text.split("BEGIN:VEVENT\r\n")[1:]:
            title = self._parse_title(item)
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(title),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=[],
                # Use actual calendar page for source
                source="https://www.detroitk12.org/Page/9425",
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_line = re.search(r"(?<=SUMMARY\:).*(?=CLASS\:)", item, flags=re.DOTALL).group()
        # Remove newlines where text is cut off
        return re.sub(r"\n\s+|(\(Open\))", "", title_line).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        if "hearing" in title.lower() or "community meeting" in title.lower():
            return FORUM
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_line = re.search(r"(?<=DTSTART\:)[\dTZ]{16}", item).group()
        return self._parse_datetime(start_line)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end_line = re.search(r"(?<=DTEND\:)[\dTZ]{16}", item).group()
        return self._parse_datetime(end_line)

    def _parse_datetime(self, dt_str):
        """Parse iCal datetime string in UTC into a naive datetime in local time"""
        dt = datetime.strptime(dt_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=pytz.utc)
        tz = pytz.timezone(self.timezone)
        return dt.astimezone(tz).replace(tzinfo=None)

    def _parse_location(self, item):
        """Parse or generate location."""
        loc_line = re.search(r"(?<=LOCATION\:).*(?=STATUS\:)", item, flags=re.DOTALL).group()
        # Remove newlines where text is cut off
        loc_text = re.sub(r"\r\n\s+", "", loc_line).strip()
        if "detroit" not in loc_text.lower():
            loc_text += " Detroit, MI"
        # Name is present, but in an inconsistent format so defaulting to address to be safe
        return {
            "address": loc_text,
            "name": "",
        }
