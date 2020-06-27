from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlCapitalDevelopmentSpider(CityScrapersSpider):
    name = "il_capital_development"
    agency = "Illinois Capital Development Board"
    timezone = "America/Chicago"
    start_urls = ["https://www2.illinois.gov/cdb/about/boardmeetings"]
    location = {
        "name": "James R. Thompson Center",
        "address": "100 West Randolph Street, 14th Floor, Chicago, IL 60601",
    }

    def parse(self, response):
        for item in response.xpath("//tbody/tr"):
            self._validate_location(item)
            meeting = Meeting(
                title="Capital Development Board",
                description="",
                classification=BOARD,
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes="",
                location=self.location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(
                meeting, text=" ".join(item.css("td *::text").extract())
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_date = item.xpath(".//th/text()").get()
        start_time = item.xpath(".//th/text()[preceding-sibling::br]").get()
        start = datetime.strptime(start_date + start_time, "%B %d, %Y %H:%M %p")
        return start

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end_date = item.xpath(".//th/text()").get()
        end_time = "12:00 AM"
        end = datetime.strptime(end_date + end_time, "%B %d, %Y %H:%M %p")
        end += timedelta(days=1)
        return end

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _validate_location(self, item):
        """Validate if location has changed"""
        if "Chicago" not in " ".join(item.css("td *::text").extract()):
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for href in item.xpath(".//ul/li/a"):
            links.append(
                {
                    "title": href.xpath("text()").get().strip(),
                    "href": href.xpath("@href").get().strip(),
                }
            )
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
