import re
from datetime import datetime

from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    COMMITTEE,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlCommerceSpider(CityScrapersSpider):
    name = "il_commerce"
    agency = "Illinois Commerce Commission"
    timezone = "America/Chicago"
    start_urls = [
        # Returns a page with 32 days of meetings from today's date, including today.
        "https://www.icc.illinois.gov/meetings?dts=32&scm=True&sps=True&sh=True&sjc=True&ssh=False&smceb=True"  # noqa
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
            yield response.follow(href, callback=self._parse_event_page)

    def _parse_event_page(self, response):
        panel = response.css(".soi-icc-container > .row > .col-12")
        start = self._parse_start(panel)
        if start is None:
            self.logger.warning("Could not parse start time from %s", response.url)
            return
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(panel),
            classification=self._parse_classification(title),
            start=start,
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
        """
        Parse or generate meeting title. The h2 holds the body's name followed by a
        span with the meeting name. For the Commission itself, use the meeting name
        (e.g. "Regular Open Meeting"). For other bodies, use the body's name, since
        the span only repeats it (e.g. "Motor Carrier Employee Board Meeting").
        """
        body_str = " ".join(selector.css(".soi-container h2::text").extract()).strip()
        meeting_str = " ".join(
            selector.css(".soi-container h2 span *::text").extract()
        ).strip()
        body_str = re.sub(r"\s+", " ", body_str)
        meeting_str = re.sub(r"\s+", " ", meeting_str)
        if body_str and body_str != self.agency:
            return body_str
        return meeting_str

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
        if "board" in title.lower():
            return BOARD
        return COMMISSION

    def _parse_start(self, selector):
        """
        Parse start datetime as a naive datetime object. The page shows the date as
        "October 15, 2026 at 11:30 AM", and the time used to sit in a separate span
        without the "at", so the word is optional. Returns None if no date is found.
        """
        start_str = re.sub(
            r"\s+", " ", " ".join(selector.css("h3.mt-4 *::text").extract())
        )
        match = re.search(
            r"([A-Z][a-z]{2,8} \d{1,2}, \d{4}) (?:at )?(\d{1,2}:\d{2} [AP]M)",
            start_str,
        )
        if not match:
            return None
        return datetime.strptime(" ".join(match.groups()), "%B %d, %Y %I:%M %p")

    def _parse_location(self, selector):
        """Parse or generate location."""
        location_block = selector.css(".row.mt-4 > .col-12")
        if len(location_block) == 0:
            return {
                "address": "",
                "name": "TBD",
            }
        location_items = location_block[0].css("p *::text").extract()
        if not "".join(location_items).strip():
            # Some meetings list only a place name, such as a video conference
            name = " ".join(location_block[0].css("h4 *::text").extract()).strip()
            return {
                "address": "",
                "name": name or "TBD",
            }
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
