import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookNorthShoreMosquitoSpider(CityScrapersSpider):
    name = "cook_north_shore_mosquito"
    agency = "Cook County North Shore Mosquito Abatement District"
    timezone = "America/Chicago"
    start_urls = ["https://www.nsmad.com/news-events/board-meetings/"]
    location = {
        "address": "117 Northfield Road, Northfield, IL 60093",
        "name": "NSMAD Office",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        cal_title = response.css(".entry-content h2::text").extract_first()
        year_str = re.search(r"\d{4}", cal_title).group()

        for item in response.css(".entry-content li li"):
            meeting = Meeting(
                title="Board of Trustees",
                description="",
                classification=BOARD,
                start=self._parse_start(item, year_str),
                end=None,
                all_day=False,
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(
                meeting, text=item.css("::text").extract_first()
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item, year_str):
        """Parse start datetime as a naive datetime object."""
        date_str = re.search(
            r"[A-Za-z]{3,10} \d{1,2}", item.css("::text").extract_first()
        ).group()
        return datetime.strptime(" ".join([date_str, year_str, "7pm"]), "%B %d %Y %I%p")

    def _validate_location(self, response):
        """Parse or generate location."""
        if "117 North" not in " ".join(
            response.css(".entry-content p::text").extract()
        ):
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            link_title = link.css("::text").extract_first()
            links.append(
                {
                    "title": "Minutes" if "Minutes" in link_title else "Agenda",
                    "href": link.attrib["href"],
                }
            )
        return links
