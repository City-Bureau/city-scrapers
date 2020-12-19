import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa20Spider(CityScrapersSpider):
    name = "chi_ssa_20"
    agency = "Chicago Special Service Area #20 South Western Avenue"
    timezone = "America/Chicago"
    start_urls = ["https://www.mpbhba.org/business-resources/"]
    location = {
        "name": "Beverly Bank & Trust",
        "address": "10258 S Western Ave, Chicago, IL 60643",
    }

    def parse(self, response):

        base = response.xpath(
            "//*[self::p or self::strong or self::h3]/text()"
        ).getall()


        for index, line in enumerate(base):
            if "ssa meetings" in line.lower():
                del base[:index]

        for index, line in enumerate(base):
            if "ssa 64" in line.lower():
                del base[index:]

        for item in base:
            if re.match(r"^\D*\d{4}\D*$", item):
                year = re.match(r"^\d{4}", item)[0]

        for item in base:

            item = re.sub(r"\s+", " ", item).lower()

            if re.match(r"^\s*$", item):
                continue

            start = self._parse_start(item, year)
            if not start:
                continue

            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=start,
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self.location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Commission"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item, year):

        if not any(word in item for word in ["beverly", "ssa"]):
            item=(re.sub(r"(^[a-z]+,\s+)" , "", item).strip())
            item=re.sub(r"[,\.]", "", item)
            ready_date = item + " " + year
            date_object = datetime.strptime(ready_date, "%B %d %I %p %Y")
            return date_object

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
