import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa2Spider(CityScrapersSpider):
    name = "chi_ssa_2"
    agency = "Chicago Special Service Area #2 Belmont/Central"
    timezone = "America/Chicago"
    start_urls = ["http://belmontcentral.org/about-ssa-2/ssa2-meeting-minutes-audit/"]
    location = {
        "address": "5534 W. Belmont Avenue Chicago, IL 60641",
        "name": "Belmont-Central Chamber of Commerce",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".entry-content a"):
            start = self._parse_start(item)
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
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        text = item.css("*::text").extract_first()
        date = re.search(r"\d{1,2}-\d{1,2}-\d{4}", text)
        if date:
            parsed_date = datetime.strptime(date.group(), "%m-%d-%Y")
            return datetime.combine(parsed_date.date(), time(14))

    def _parse_links(self, item):
        """Parse or generate links."""
        link = item.css("*::attr(href)").extract_first()
        return [{"href": link, "title": "Minutes"}]
