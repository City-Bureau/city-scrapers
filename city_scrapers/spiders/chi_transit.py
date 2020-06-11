import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiTransitSpider(CityScrapersSpider):
    name = "chi_transit"
    agency = "Chicago Transit Authority"
    timezone = "America/Chicago"
    base_url = "http://www.transitchicago.com"
    start_urls = ["https://www.transitchicago.com/board/notices-agendas-minutes/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        response_items = response.css(".agendaminuteDataTbl tr:not(:first-child)")
        for idx, item in enumerate(response_items):
            # Including previous item for meetings where it's needed
            prev_item = response_items[idx - 1] if idx > 0 else None
            start_datetime = self._parse_start(item, prev_item)
            if start_datetime:
                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=self._parse_classification(item),
                    start=start_datetime,
                    end=self._parse_end(start_datetime),
                    time_notes="End estimated 3 hours after start time",
                    all_day=False,
                    location=self._parse_location(item),
                    links=self._parse_links(item),
                    source=self._parse_source(response),
                )
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_classification(self, item):
        """Classify meeting as board or committee meetings."""
        name = item.css("td:nth-child(3)::text").extract_first().lower()
        if "board" in name:
            return BOARD
        else:
            return COMMITTEE

    def _parse_location(self, item):
        """Parse or generate location."""
        location_str = " ".join(item.css("td:nth-child(4)::text").extract())
        # Always 537 W Lake, so handle that if provided (but allow for change)
        if location_str and (
            re.search(
                r"567 (W.|W|West) Lake.*|board\s?room", location_str, re.IGNORECASE,
            )
            or re.search(r"cta.*board.*room", location_str, re.IGNORECASE)
        ):
            return {
                "name": "Chicago Transit Authority 2nd Floor Boardroom",
                "address": "567 West Lake Street Chicago, IL 60661",
            }
        elif location_str:
            loc = (
                location_str.replace("CTA Headquarters", "")
                .replace(" ,", "")
                .strip()
                .rstrip(",")
            )
            return {
                "name": "",
                "address": re.sub(r"[\s\n]+", " ", loc).strip(),
            }

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css("td:nth-child(3)::text").extract_first()

    def _parse_links(self, item):
        """Add meeting notice and agenda to links"""
        links = []
        link_items = item.css("td:last-child a")
        for link in link_items:
            links.append(
                {
                    "href": self.base_url + link.xpath("./@href").extract_first(),
                    "title": link.xpath("./text()").extract_first(),
                }
            )
        return links

    def _parse_start(self, item, prev_item=None):
        """Parse start datetime as a naive datetime object."""
        date_el_text = item.css("td:first-child").extract_first()
        date_text = date_el_text[4:-5]
        date_str, time_str = [x.strip() for x in date_text.split("<br>")]
        # A.M. and AM formats are used inconsistently, remove periods
        time_str = time_str.replace(".", "")
        if re.match(r"\d{1,2}:\d{2} (AM|PM)", time_str):
            return datetime.strptime(date_str + time_str, "%m/%d/%Y%I:%M %p")
        # "Immediately after" specific meeting used frequently, return the
        # start time of the previous meeting
        elif prev_item is not None:
            return self._parse_start(prev_item)

    def _parse_end(self, start_datetime):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return start_datetime + timedelta(hours=3)

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
