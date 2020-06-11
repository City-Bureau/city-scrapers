import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiInfrastructureTrustSpider(CityScrapersSpider):
    name = "chi_infrastructure_trust"
    agency = "Chicago Infrastructure Trust"
    timezone = "America/Chicago"
    start_urls = [
        "http://chicagoinfrastructure.org/public-records/meeting-records-2/",
        "http://chicagoinfrastructure.org/public-records/scheduled-meetings/",
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for item in response.css(".entry p"):
            if item.xpath(".//span"):
                continue

            start = self._parse_start(item, response)
            if not start or (
                start < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
            ):
                return

            meeting = Meeting(
                title="Board of Directors",
                description="",
                classification=BOARD,
                start=start,
                end=None,
                all_day=False,
                time_notes="Confirm details in meeting documents",
                location=self._parse_location(start),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item, response):
        """Parse start datetime as a naive datetime object."""
        item_text = re.sub(r"\s+", " ", " ".join(item.css("*::text").extract())).strip()
        date_match = re.search(r"[A-Z][a-z]{2,8} \d{1,2},? \d{4}", item_text)
        if date_match:
            date_str = date_match.group().replace(",", "")
            return datetime.strptime(date_str, "%B %d %Y")
        else:
            header_str = " ".join(
                response.css(".entry strong")[0].css("*::text").extract()
            ).strip()
            year_match = re.search(r"\d{4}", header_str)
            if not year_match:
                return

            date_match = re.search(r"[A-Z][a-z]{2,8} \d{1,2}", item_text)
            if not date_match:
                return

            return datetime.strptime(
                " ".join([date_match.group(), year_match.group()]), "%B %d %Y"
            )

    def _parse_location(self, start):
        """Parse or generate location."""
        # Not a clean fix, but changing the address after a certain date
        if start > datetime(2019, 11, 1):
            return {
                "name": "",
                "address": "35 E Wacker Dr, Chicago, IL 60601",
            }
        else:
            return {
                "name": "Metropolitan Planning Council",
                "address": "140 South Dearborn Street, Suite 1400, Chicago, IL 60603",
            }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for link in item.xpath("./following-sibling::ul[1]/li/a"):
            links.append(
                {
                    "href": link.attrib["href"],
                    "title": " ".join(link.css("*::text").extract()),
                }
            )
        return links
