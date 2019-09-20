from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiMidwayNoiseSpider(CityScrapersSpider):
    name = "chi_midway_noise"
    agency = "Chicago Midway Noise Compatibility Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.flychicago.com"]
    start_urls = ["https://www.flychicago.com"]
    location = {
        "name": "The Mayfield",
        "address": "6072 S. Archer Ave., Chicago, IL 60638",
    }
    source = "https://www.flychicago.com/community/MDWnoise/AdditionalResources/pages/default.aspx"

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".meetings"):
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=COMMISSION,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="Start times are not explicitly stated, but all observed past meetings occurred at 6:30PM",
                location=self.location,
                links=self._parse_links(item),
                source=self.source,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]
