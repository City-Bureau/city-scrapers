import re
from datetime import datetime
from typing import Mapping

from city_scrapers_core.constants import CANCELLED, COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiBoardElectionsSpider(CityScrapersSpider):
    name = "chi_board_elections"
    agency = "Chicago Board of Elections"
    timezone = "America/Chicago"
    start_urls = [
        "https://chicagoelections.gov/about-board/board-meetings",
    ]
    location = {
        "name": "Board's Conference Room",
        "address": "Suite 800, 69 West Washington Street, Chicago, Illinois",
    }

    def parse(self, response):
        events = response.css(".views-row article")
        for event in events:
            meeting = Meeting(
                title=self._parse_title(event),
                description="",
                classification=COMMISSION,
                start=self._parse_start(event),
                end=None,
                time_notes="",
                all_day=False,
                location=self.location,
                links=self._parse_links(event),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, event):
        return event.css("article > h3 > span::text").extract_first()

    def _parse_start(self, event):
        date_string = event.css(".board-meeting--teaser p::text").extract_first()
        date = re.search(r"\w+\s\d+,\s\d{4}", date_string).group()
        start_time = datetime.strptime(date, "%B %d, %Y").replace(
            hour=10, minute=0, second=0
        )
        return start_time

    def _parse_links(self, event):
        links = []
        for atag in event.css("a"):
            links.append(
                {
                    "title": atag.css("::text").extract_first(),
                    "href": atag.css("::attr(href)").extract_first(),
                }
            )
        return links

    def _get_status(self, item: Mapping, text: str = "") -> str:
        """
        We need to override the parent class's handling of cancellation because this agency
        uses the word "rescheduled" in titles to indicate a meeting has been set to a new date,
        not cancelled.
        """
        meeting_text = " ".join(
            [item.get("title", ""), item.get("description", ""), text]
        ).lower()
        if any(word in meeting_text for word in ["cancel", "postpone"]):
            return CANCELLED
        if item["start"] < datetime.now():
            return PASSED
        return TENTATIVE
