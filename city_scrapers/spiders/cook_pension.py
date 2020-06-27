import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookPensionSpider(CityScrapersSpider):
    name = "cook_pension"
    agency = "Cook County Pension Fund"
    timezone = "America/Chicago"
    start_urls = ["https://www.cookcountypension.com/agendaminutes/"]
    location = {
        "name": "Cook County Pension Fund Office",
        "address": "70 W Madison St, Suite 1925, Chicago, IL 60602",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Create a mapping of IDs to meetings to only return unique meeting, group links
        meeting_id_map = {}
        for item in response.css(".datatbl tr")[1:]:
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
                start=self._parse_start(item, title),
                end=None,
                all_day=False,
                time_notes="See agenda to confirm times",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            # Add newly-found links to meeting if exists, otherwise add to dictionary
            if meeting["id"] in meeting_id_map:
                meeting_id_map[meeting["id"]]["links"].extend(meeting["links"])
            else:
                meeting_id_map[meeting["id"]] = meeting

        # Yield each unique meeting
        for meeting in meeting_id_map.values():
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = " ".join(item.css("td:nth-child(3)::text").extract()).strip()
        return re.sub(r"[\d\.]", "", title_str).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "board" in title.lower():
            return BOARD
        return COMMITTEE

    def _parse_start(self, item, title):
        """Parse start datetime as a naive datetime object."""
        time_obj = time(9, 30)
        if "legislative" in title.lower():
            time_obj = time(8, 30)
        date_str = " ".join(item.css("td:nth-child(1) *::text").extract()).strip()
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
        return datetime.combine(date_obj, time_obj)

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "href": response.urljoin(link.attrib["href"]),
                    "title": " ".join(link.css("*::text").extract()).strip(),
                }
            )
        return links
