import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiMunicipalRetirementSpider(CityScrapersSpider):
    name = "chi_municipal_retirement"
    agency = "Municipal Employees' Annuity and Benefit Fund of Chicago"
    timezone = "America/Chicago"
    start_urls = ["https://www.meabf.org/retirement-board/minutes"]
    location = {
        "name": "Fund Office",
        "address": "321 N Clark St, Suite 700, Chicago, IL 60654",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._parse_location(response)
        for item in response.css(".data_row:not(.data_head)"):
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="See agenda to confirm time",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = " ".join(item.css("div:nth-child(2)::text").extract()).strip()
        if "reg" in title_str.lower():
            return "Retirement Board"
        return title_str

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "Board" in title:
            return BOARD
        return COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_str = " ".join(item.css("div:first-child::text").extract()).strip()
        date_obj = datetime.strptime(date_str, "%B %d, %Y").date()
        # Default to 9 AM time unless other time shows up in the description
        time_obj = time(9)
        desc_str = " ".join(item.css("div:nth-child(2)::text").extract()).strip()
        time_match = re.search(r"\d{1,2}:\d{1,2} [apmAPM\.]{2,4}", desc_str)
        if time_match:
            time_str = time_match.group().upper().replace(".", "").strip()
            time_obj = datetime.strptime(time_str, "%I:%M %p").time()
        return datetime.combine(date_obj, time_obj)

    def _parse_location(self, response):
        """Parse or generate location."""
        if "321 N" not in " ".join(
            response.css("#content-container p::text").extract()
        ):
            raise ValueError("Meeting location has changed")

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
