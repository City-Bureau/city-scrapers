import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlEnvironmentalJusticeSpider(CityScrapersSpider):
    name = "il_environmental_justice"
    agency = "Illinois Commission on Environmental Justice"
    timezone = "America/Chicago"
    start_urls = [
        "https://www2.illinois.gov/epa/topics/environmental-justice/commission/Pages/meetings.aspx"  # noqa
    ]
    location = {
        "name": "James R Thompson Center",
        "address": "100 W Randolph St, Room 512 Chicago, IL 60601",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        title = "Commission"
        date_str = ""
        year_str = ""
        for item in response.css(".ms-rtestate-field > *"):
            # Iterate through immediate children of content, check tag for next steps
            if item.root.tag == "h2":
                title = item.xpath("./text()").extract_first()
                continue
            if item.root.tag == "h3":
                year_str = item.xpath("./text()").extract_first()
                continue
            # Ignore link lists that are siblings instead of children
            if item.root.tag == "ul" and len(item.xpath("./li/a")) > 0:
                continue
            if item.root.tag == "div":
                list_items = item.css("ul")
                if len(list_items) > 0:
                    list_item = list_items[0]
                else:
                    continue
            elif item.root.tag == "ul":
                list_item = item
            else:
                continue

            for date_item in list_item.xpath("./li"):
                date_str = (date_item.xpath("./text()").extract_first() or "").strip()
                if not date_str:
                    continue
                meeting = Meeting(
                    title=title,
                    description="",
                    classification=self._parse_classification(title),
                    start=self._parse_start(date_str, year_str),
                    end=None,
                    all_day=False,
                    time_notes="See agenda to confirm details",
                    location=self.location,
                    links=self._parse_links(item, date_item, response),
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        return COMMISSION

    def _parse_start(self, date_str, year_str):
        """Parse start datetime as a naive datetime object."""
        # Using the earlier time, even though it's typically at 10am
        date_match = re.search(r"[a-zA-Z]{3,10}\s+\d{1,2}", date_str)
        if not date_match:
            return
        return datetime.strptime(
            "{} {} 9:30".format(date_match.group(), year_str), "%B %d %Y %H:%M"
        )

    def _parse_links(self, item, date_item, response):
        """
        Parse or generate links. Checks combinations of elements and selectors, return
        the first that's successful
        """
        links = []
        for el, sel in [
            (date_item, "./ul/li/a"),
            (date_item, "./following-sibling::ul[1]/li/a"),
            (date_item, "./following-sibling::li[1]/ul/li/a"),
            (item, "./ul/li/a"),
            (item, "./following-sibling::ul[1]/li/a"),
            (item, "./following-sibling::li[1]/ul/li/a"),
        ]:
            for link in el.xpath(sel):
                links.append(
                    {
                        "title": link.css("*::text").extract_first().strip(),
                        "href": response.urljoin(link.attrib["href"]),
                    }
                )
            if len(links) > 0:
                return links
        return links
