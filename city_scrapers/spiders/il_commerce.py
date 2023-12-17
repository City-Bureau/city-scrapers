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
        # Returns a page with 32 days of meetings from today's date, including today.
        "https://www.icc.illinois.gov/meetings?dts=32&scm=True&sps=True&sh=True&sjc=True&ssh=False&smceb=True"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        event_links = response.css(".p-2 a.day")
        for event_link in event_links:
            href = event_link.attrib["href"]
            yield response.follow(
                href, callback=self._parse_event_page
            )

    def _parse_event_page(self, response):
        panel = response.css(".soi-icc-container .col-12")
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(panel),
            classification=self._parse_classification(title),
            start=self._parse_start(panel),
            end=None,
            all_day=False,
            time_notes="",
            location=self._parse_location(panel),
            links=self._parse_links(panel, response),
            source=response.url,
        )
        status_str = " ".join(response.css("h3 *::text").extract())
        meeting["status"] = self._get_status(meeting, text=status_str)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, selector):
        """Parse or generate meeting title."""
        title_str = re.sub(
            r"\s+", " ", " ".join(selector.css(".soi-container h2 *::text").extract())
        ).strip()
        return re.sub(
            r"(Illinois Commerce Commission|(?=Committee )Committee Meeting$)",
            "",
            title_str,
        ).strip()

    def _parse_description(self, selector):
        """Parse or generate meeting description."""
        return re.sub(
            r"\s+", " ", " ".join(selector.css(".mt-4+ p *::text").extract())
        ).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "advisory" in title.lower():
            return ADVISORY_COMMITTEE
        if "committee" in title.lower():
            return COMMITTEE
        return COMMISSION

    def _parse_start(self, selector):
        """Parse start datetime as a naive datetime object."""
        start_str = " ".join(selector.css("h3.mt-4 *::text").extract())
        dt_str = re.search(
            r"[A-Z][a-z]{2,8} \d{1,2}, \d{4} \d{1,2}:\d{2} [APM]{2}", start_str
        ).group()
        return datetime.strptime(dt_str, "%B %d, %Y %I:%M %p")

    def _parse_location(self, selector):
        """Parse or generate location."""
        location_block = selector.css(".row.mt-4 > .col-12")
        if len(location_block) == 0:
            return {
                "address": "",
                "name": "TBD",
            }
        location_items = location_block[0].css("p *::text").extract()
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

    def _parse_links(self, selector, response):
        """Parse or generate links."""
        links = selector.css(".row.mt-4 .list-unstyled a")
        urls = []
        if not links:
            return urls
        for link in links:
            urls.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return urls
