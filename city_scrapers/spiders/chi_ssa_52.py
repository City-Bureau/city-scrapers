import re
from datetime import datetime
from difflib import SequenceMatcher

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa52Spider(CityScrapersSpider):
    name = "chi_ssa_52"
    agency = "Chicago Special Service Area #52 51st Street"
    timezone = "America/Chicago"
    start_urls = ["https://www.51ststreetchicago.com/about.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        items = response.css("div.paragraph")[3:4]
        title = items.css("strong::text").get()
        meeting = items.css("ul")[0]

        item = (title, meeting)

        for meet in meeting.css("li"):
            meet = self._clean_meet(meet)

            meeting = Meeting(
                title=self._parse_title(title),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(meet),
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

    def _clean_meet(self, meet):
        """Clean a meet datetime info and group the info"""
        meet = meet.css("::text").get()
        meet = meet.replace("\xa0", "")

        clean_str = re.sub(r"[^\w:]+", " ", meet)
        meet_info = clean_str.split()

        return meet_info

    def _check_am_pm(self, time):
        time = time.split(":")
        hour = time[0]
        minutes = time[1]

        if int(hour) >= 8 and int(hour) <= 12:
            return f"{hour}:{minutes} AM"
        return f"{hour}:{minutes} PM"

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        # item = item.replace("\xa0", "").strip()
        return COMMISSION

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        months = [
            "JANUARY",
            "FEBRUARY",
            "MARCH",
            "APRIL",
            "MAY",
            "JUNE",
            "JULY",
            "AUGUST",
            "SEPTEMBER",
            "OCTOBER",
            "NOVEMBER",
            "DECEMBER",
        ]

        time = item[4]
        time = self._check_am_pm(time)

        try:
            date = datetime.strptime(
                f"{item[2]} {item[1]} {item[3]} {time}", "%d %B %Y %I:%M %p",
            )
        except ValueError:
            for month in months:
                ratio = SequenceMatcher(None, month, item[1]).ratio()
                if ratio > 0.5:
                    date = datetime.strptime(
                        f"{item[2]} {month} {item[3]} {time}", "%d %B %Y %I:%M %p",
                    )
        return date

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
        return {
            "address": "220 E 51st St Chicago, IL 60615",
            "name": "51st Street Business Association",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return []

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
