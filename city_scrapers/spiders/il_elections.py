from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

from datetime import datetime
from urllib.parse import urljoin


class IlElectionsSpider(CityScrapersSpider):
    name = "il_elections"
    agency = "Illinois State Board of Elections"
    timezone = "America/Chicago"
    start_urls = ["https://www.elections.il.gov/AboutTheBoard/Agenda.aspx"]
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meetings = response.css(".SearchListTable").xpath("./tr")[1:-1]

        # dates = response.css(".SearchListTable").xpath("//tr/td[1]").re(r"[A-Z][a-z]{2}, .*20\d\d")

        for item in meetings:
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item, response),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Illinois State Board of Elections"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        desc = item.xpath("./td[4]/text()").extract_first().strip()
        return desc

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.xpath("./td[1]").re(r"[A-Z][a-z]{2}, .*20\d\d")[0]
        time = item.xpath("./td[2]").re(r"\d{2}:\d{2} [a|p].m")[0].replace(".", "")
        dt = date + " " + time
        return datetime.strptime(dt, "%a, %B %d, %Y %I:%M %p")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        name = item.xpath("./td[3]/text()").extract_first()
        return {
            "address": "",
            "name": name,
        }

    def _parse_links(self, item, response):
        """Parse or generate links."""
        href = item.xpath("./td[1]//@href").extract_first()
        href = urljoin(response.url, href)
        return [{"href": href, "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
