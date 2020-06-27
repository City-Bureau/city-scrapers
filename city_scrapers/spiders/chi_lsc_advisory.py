import re
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLscAdvisorySpider(CityScrapersSpider):
    name = "chi_lsc_advisory"
    agency = "Chicago Local School Council Advisory Board"
    timezone = "America/Chicago"
    start_urls = ["https://cps.edu/lscrelations/Pages/LSCAB.aspx"]
    location = {
        "name": "Garfield Center",
        "address": "2651 W Washington Blvd, Chicago, IL 60612",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        bold_text = " ".join(response.css(".inpage-resets strong *::text").extract())
        self._validate_location(bold_text)

        time_match = re.search(r"\d{1,2}:\d{2}[apm]{2}", bold_text)
        if not time_match:
            raise ValueError("Could not find meeting start time")
        time_str = time_match.group()
        year = int(re.search(r"\d{4}-\d{4}", bold_text).group().split("-")[0])

        for item in response.css(".inpage-resets tr"):
            start = self._parse_start(item, time_str, str(year))
            if not start:
                continue
            # If the month is before September it's the second half of the school year
            if start.month < 9:
                start = start.replace(year=year + 1)
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=ADVISORY_COMMITTEE,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(
                meeting, text=" ".join(item.css("*::text").extract())
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Check for additional info in row"""
        title_str = " ".join(item.css("td:first-child *::text").extract()).strip()
        content_match = re.search(r"(?<=\().*(?=\))", title_str)
        if not content_match:
            return "Advisory Board"
        return content_match.group().title()

    def _parse_start(self, item, time_str, year_str):
        """Parse start datetime as a naive datetime object."""
        start_str = " ".join(item.css("td:first-child *::text").extract()).strip()
        date_match = re.search(r"[A-Z][a-z]{2,8} \d{1,2}", start_str)
        if not date_match:
            return
        return datetime.strptime(
            " ".join([date_match.group(), time_str, year_str]), "%B %d %I:%M%p %Y"
        )

    def _validate_location(self, text):
        """Parse or generate location."""
        if "2651" not in text:
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links
