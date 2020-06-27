import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa34Spider(CityScrapersSpider):
    name = "chi_ssa_34"
    agency = "Chicago Special Service Area #34 Uptown"
    timezone = "America/Chicago"
    start_urls = ["https://exploreuptown.org/ssa/"]
    custom_settings = {"ROBOTSTXT_OBEY": False}
    location = {
        "name": "Bridgeview Bank",
        "address": "4753 N Broadway, First Floor Conference Room, Chicago, Illinois 60640",  # noqa
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        meeting_dt_list = []
        for item in response.css(
            ".entry-content li::text, .entry-content h5 + p::text"
        ).extract():
            start = self._parse_start(item)
            if not start or start in meeting_dt_list:
                continue
            meeting_dt_list.append(start)
            meeting = Meeting(
                title="Advisory Commission",
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(start, response),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        if not item or not re.search(r"\d{4}", item):
            return
        dt_str = re.sub(r"(.*day, |(?<=\d)[a-l-n-z]{2}|[,–])", "", item.strip()).strip()
        return datetime.strptime(
            re.sub(r"\s+", " ", dt_str).strip(), "%B %d %Y %I:%M%p"
        )

    def _validate_location(self, response):
        if "4753 N" not in " ".join(response.css(".entry-content *::text").extract()):
            raise ValueError("Meeting location has changed")

    def _parse_links(self, start, response):
        """Parse or generate links."""
        links = []
        # Links follow a uniform structure, so search for this pattern by date
        for link in response.css("a[href*='{}']".format(start.strftime("%Y-%m%d"))):
            links.append(
                {
                    "title": "Agenda"
                    if "agenda" in link.attrib["href"].lower()
                    else "Minutes",
                    "href": link.attrib["href"],
                }
            )
        return links
