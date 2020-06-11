import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLandTrustSpider(CityScrapersSpider):
    name = "chi_land_trust"
    agency = "Chicago Community Land Trust"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/doh/supp_info/chicago_communitylandtrust0.html"  # noqa
    ]
    location = {
        "name": "City Hall",
        "address": "121 N LaSalle St, #1003A Chicago, IL 60602",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # TODO: Committees
        for item in response.css(".page-full-description .col-xs-12 > *"):
            if item.css("strong"):
                year_match = re.search(
                    r"\d{4}", item.css("strong::text").extract_first()
                )
                if year_match:
                    year_str = year_match.group()
            date_map = {}
            active_key = None
            for content in item.css("td::text, td a"):
                if isinstance(content.root, str) and content.root.strip():
                    date_map[content.root] = []
                    active_key = content.root
                else:
                    date_map[active_key].append(content)

            for date_str, links in date_map.items():
                start = self._parse_start(date_str, year_str)
                if not start:
                    continue
                meeting = Meeting(
                    title="Board of Directors",
                    description="",
                    # TODO: Figure out committees
                    classification=BOARD,
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="See agenda to confirm time",
                    location=self.location,
                    links=self._parse_links(links, response),
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting, text=date_str)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_start(self, date_str, year_str):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(
            "{} {} 9AM".format(date_str.strip(), year_str), "%B %d %Y %I%p"
        )

    def _parse_links(self, link_items, response):
        """Parse or generate links."""
        links = []
        for link_item in link_items:
            if hasattr(link_item, "attrib") and link_item.attrib.get("href"):
                links.append(
                    {
                        "href": response.urljoin(link_item.attrib["href"]),
                        "title": link_item.css("::text").extract_first(),
                    }
                )
        return links
