import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa4Spider(CityScrapersSpider):
    name = "chi_ssa_4"
    agency = "Chicago Special Service Area #4 South Western Avenue"
    timezone = "America/Chicago"
    start_urls = ["https://95thstreetba.org/about/ssa-4/"]
    location = {"name": "", "address": "10437 S Western Ave Chicago, IL 60643"}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # TODO: Get minutes once an example is posted
        location = self.location
        for row in response.css(".et_pb_row_2"):
            for idx, item in enumerate(row.css("p")):
                item_text = " ".join(item.css("*::text").extract())
                if idx == 0:
                    if "Zoom" in item_text:
                        location = {"name": "Virtual Meeting", "address": ""}
                    elif "10437" not in item_text:
                        raise ValueError("Meeting location has changed")
                    continue
                start = self._parse_start(item_text)
                if not start:
                    continue
                meeting = Meeting(
                    title="Commission",
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=location,
                    links=self._parse_links(response),
                    source=response.url,
                )

                meeting["status"] = self.get_status(meeting, text=item_text)
                meeting["id"] = self.get_id(meeting)
                yield meeting

    def _parse_start(self, item_text):
        """Parse start datetime as a naive datetime object."""
        date_match = re.search(r"[A-Z][a-z]{2,9} \d\d?,? \d{4}", item_text)
        time_match = re.search(r"\d\d?:\d\d ?[apm\.]{2,4}", item_text)
        time_str = "12:00am"
        if time_match:
            time_str = time_match.group().replace(" ", "").replace(".", "")
        if not date_match:
            return
        date_str = date_match.group().replace(",", "")
        return datetime.strptime(f"{date_str} {time_str}", "%B %d %Y %I:%M%p")

    def _parse_links(self, response):
        """Parse or generate links."""
        # TODO: Implement once there are examples
        return []
