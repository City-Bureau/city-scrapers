import re
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE, COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlCommerceSpider(CityScrapersSpider):
    name = "il_commerce"
    agency = "Illinois Commerce Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.icc.illinois.gov/meetings/default.aspx?dts=32&et=1&et=5&et=3"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for nav_link in response.css(".col-sm-7 a.btn"):
            if "?bd=" in nav_link.attrib["href"]:
                yield response.follow(
                    nav_link.attrib["href"], callback=self._parse_events_page
                )

        yield from self._parse_events_page(response)

    def _parse_events_page(self, response):
        for item in response.css(".panel-body a"):
            yield response.follow(item.attrib["href"], callback=self._parse_detail)

    def _parse_detail(self, response):
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(response),
            classification=self._parse_classification(title),
            start=self._parse_start(response),
            end=None,
            all_day=False,
            time_notes="",
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )

        meeting["status"] = self._get_status(
            meeting, text=" ".join(response.css(".col-sm-12 *::text").extract())
        )
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        title_str = re.sub(
            r"\s+", " ", " ".join(response.css(".soi-container h2 *::text").extract())
        ).strip()
        return re.sub(
            r"(Illinois Commerce Commission|(?=Committee )Committee Meeting$)",
            "",
            title_str,
        ).strip()

    def _parse_description(self, response):
        """Parse or generate meeting description."""
        return re.sub(
            r"\s+", " ", " ".join(response.css(".col-sm-12 > p *::text").extract())
        ).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "advisory" in title.lower():
            return ADVISORY_COMMITTEE
        if "committee" in title.lower():
            return COMMITTEE
        return COMMISSION

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        start_str = " ".join(response.css("h3.mt-4 *::text").extract())
        dt_str = re.search(
            r"[A-Z][a-z]{2,8} \d{1,2}, \d{4} \d{1,2}:\d{2} [APM]{2}", start_str
        ).group()
        return datetime.strptime(dt_str, "%B %d, %Y %I:%M %p")

    def _parse_location(self, response):
        """Parse or generate location."""
        location_block = response.css(".row.mt-4 > .col-12")[0]
        location_items = location_block.css("p *::text").extract()
        addr_items = [
            i.strip() for i in location_items if "Building" not in i and i.strip()
        ]
        name_items = [
            i.strip() for i in location_items if "Building" in i and i.strip()
        ]
        return {
            "address": " ".join(addr_items),
            "name": " ".join(name_items),
        }

    def _parse_links(self, response):
        """Parse or generate links."""
        links = []
        for link in response.css(".row.mt-4 .list-unstyled a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links
