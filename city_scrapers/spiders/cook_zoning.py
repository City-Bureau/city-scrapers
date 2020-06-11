import re
from datetime import datetime, time

from city_scrapers_core.constants import FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookZoningSpider(CityScrapersSpider):
    name = "cook_zoning"
    agency = "Cook County Zoning Board of Appeals"
    timezone = "America/Chicago"
    start_urls = ["https://www.cookcountyil.gov/agency/zoning-board-appeals-0"]
    location = {
        "name": "County Administration Building",
        "address": "69 W Washington St 22nd Floor Conference Room, Chicago, IL 60602",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        hearing_list = response.css(".field-item ul")[1]
        for item in hearing_list.css("li"):
            item_text = " ".join(item.css("*::text").extract())
            meeting = Meeting(
                title="Public Hearing",
                description="",
                classification=FORUM,
                start=self._parse_start(item_text),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting, text=item_text)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, text):
        """Parse start datetime as a naive datetime object."""
        date_match = re.search(r"[a-zA-Z]{3,10} \d{1,2},? \d{4}", text)
        if not date_match:
            return
        date_str = date_match.group().replace(",", "")
        date_obj = datetime.strptime(date_str, "%B %d %Y").date()
        return datetime.combine(date_obj, time(13))

    def _validate_location(self, response):
        """Check if the meeting location has changed"""
        text = " ".join(response.css(".field-item p::text").extract())
        if "69 W" not in text:
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append({"title": "Agenda", "href": link.attrib["href"]})
        return links
