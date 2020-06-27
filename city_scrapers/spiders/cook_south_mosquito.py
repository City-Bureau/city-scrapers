import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookSouthMosquitoSpider(CityScrapersSpider):
    name = "cook_south_mosquito"
    agency = "South Cook County Mosquito Abatement District"
    timezone = "America/Chicago"
    start_urls = ["https://sccmad.org/"]
    location = {
        "name": "South Cook County Mosquito Abatement District Office",
        "address": "15500 Dixie Highway Harvey, IL 60426",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for year_group in response.css(
            ".s5_responsive_mobile_sidebar_sub:last-child > ul > li:first-child > ul > li"  # noqa
        ):
            year_str = year_group.css("span::text").extract_first().strip()
            for item in year_group.xpath("./ul/li"):
                item_str = item.css("span::text").extract_first()
                meeting = Meeting(
                    title="Board of Trustees",
                    description="",
                    classification=BOARD,
                    start=self._parse_start(item_str, year_str),
                    end=None,
                    all_day=False,
                    time_notes="See agenda to confirm time",
                    location=self.location,
                    links=self._parse_links(item, response),
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting, text=item_str)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_start(self, item_str, year_str):
        """Parse start datetime as a naive datetime object."""
        date_str = re.search(r"[a-zA-Z]{3,10} \d{1,2}", item_str).group()
        date_obj = datetime.strptime("{} {}".format(date_str, year_str), "%B %d %Y")
        return datetime.combine(date_obj.date(), time(16))

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": link.css("*::text").extract_first(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links
