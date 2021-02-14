import datetime

from city_scrapers_core.constants import BOARD, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthwestHomeEquitySpider(CityScrapersSpider):
    name = "chi_northwest_home_equity"
    agency = "Chicago Northwest Home Equity Assurance Program"
    timezone = "America/Chicago"
    start_urls = ["https://nwheap.com/category/meet-minutes-and-agendas/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        for item in response.xpath("//aside[@id = 'em_widget-5']/ul/li"):
            if not item.css("ul"):
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description="Upcoming Events",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        for item in response.xpath("//aside[@id = 'em_widget-3']/ul/li"):
            if not item.css("ul"):
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description="Past Meetings",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.xpath("a//text()").get()

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        if "commission" in self._parse_title(item).lower():
            return COMMISSION
        elif "board" in self._parse_title(item).lower():
            return BOARD
        else:
            return NOT_CLASSIFIED

    def _parse_date(self, item):
        date = item.xpath("ul/li/text()")[0].get()
        date = date[:-4] + date[-2:]
        return date

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        time = item.xpath("ul/li/text()")[1].get()
        start = time.split(" - ")[0]
        return datetime.datetime.strptime(
            start + " " + self._parse_date(item), "%I:%M %p %x"
        )

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        time = item.xpath("ul/li/text()")[1].get()
        end = time.split(" - ")[1]
        return datetime.datetime.strptime(
            end + " " + self._parse_date(item), "%I:%M %p %x"
        )

    def _parse_location(self, item):
        """Parse or generate location."""
        if len(item.xpath("ul/li/text()")) <= 2:
            return {
                "name": "Meeting place not mentioned",
                "address": "",
            }
        addr = (
            item.xpath("ul/li/text()")[2].get()
            + ", "
            + item.xpath("ul/li/text()")[3].get()
        )
        name = (
            "Main Office" if addr.startswith("3234 N. Central Ave") else "Unknown place"
        )
        return {
            "address": addr,
            "name": name,
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        link = item.xpath("a/@href").get()
        return [{"href": link, "title": self._parse_title(item)}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
