import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa51Spider(CityScrapersSpider):
    name = "chi_ssa_51"
    agency = "Chicago Special Service Area #51 Chatham"
    timezone = "America/Chicago"
    start_urls = ["http://www.cbatechworks.org/"]
    location = {
        "address": "806 East 78th Street, Chicago IL 60619",
        "name": "QBG Foundation",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        last_parsed_date = ""
        for item in response.css("div#element106 font"):
            """
            The date and times are contained within sibling divs that are identicals,
            so we have to continue the loop and only create the meeting until both date
            and times have been parsed.
            """
            if not last_parsed_date:
                last_parsed_date = self._parse_date(item)
                continue
            else:
                start_and_end = self._parse_time(item)
                if not start_and_end:
                    continue
                start = last_parsed_date + " " + start_and_end[0].strip()
                start = datetime.strptime(start, "%B %d, %Y %I:%M%p")
                end = last_parsed_date + " " + start_and_end[1].strip()
                end = datetime.strptime(end, "%B %d, %Y %I:%M%p")
                last_parsed_date = ""

            meeting = Meeting(
                title="Commission",
                description="",
                classification=COMMISSION,
                start=start,
                end=end,
                all_day=False,
                time_notes="",
                location=self.location,
                links=[],
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_date(self, item):
        text = item.css("*::text").extract_first()
        if text is None:
            return ""
        date = re.search(r"\w{3,9} \d{1,2}, \d{4}", text)
        if date:
            return date.group()
        return ""

    def _parse_time(self, item):
        """Parse start datetime as a naive datetime object."""
        text = item.css("*::text").extract_first()
        times = re.search(r"\d{1,2}:\d{2}[ap]m - \d{1,2}:\d{2}[ap]m", text)
        if times:
            return times.group().split("-")

    def _validate_location(self, response):
        if "806 East" not in " ".join(response.css("div#element106 *::text").extract()):
            raise ValueError("Meeting location has changed")
