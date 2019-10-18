import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class WayneEthicsBoardSpider(CityScrapersSpider):
    name = "wayne_ethics_board"
    agency = "Wayne County Ethics Board"
    timezone = "America/Detroit"
    start_urls = ["https://www.waynecounty.com/boards/ethicsboard/documents.aspx"]
    location = {
        "name": "Guardian Building",
        "address": "500 Griswold St, Hearing Room 704, Detroit, MI 48226",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for year_item in response.css(".ui.basic.vertical section > h3"):
            year = year_item.xpath("./text()").extract_first().strip()
            for item in year_item.xpath("following-sibling::table[1]").css("tbody tr"):
                start = self._parse_start(item, year)
                if start is None:
                    continue
                meeting = Meeting(
                    title="Ethics Board",
                    description="",
                    classification=BOARD,
                    start=start,
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

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object."""
        date_str = item.css("td:first-child::text").extract_first()
        if not date_str:
            return
        date_str = re.sub(r"^\w+day,\s+", "", date_str).strip().replace(".", "")
        if not re.search(r"\d{4}", date_str):
            date_str = "{}, {}".format(date_str, year)
        # Using default time, but doesn't apply to all
        try:
            return datetime.strptime(date_str, "%B %d, %Y").replace(hour=9)
        except ValueError:
            return datetime.strptime(date_str.replace("Sept", "Sep"), "%b %d, %Y").replace(hour=9)

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append({
                "href": response.urljoin(link.attrib["href"]),
                "title": link.xpath("./text()").extract_first(),
            })
        return links
