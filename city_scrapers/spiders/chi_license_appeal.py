import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLicenseAppealSpider(CityScrapersSpider):
    name = "chi_license_appeal"
    agency = "Chicago License Appeal Commission"
    timezone = "America/Chicago"
    start_urls = ["https://www.chicago.gov/city/en/depts/lac/supp_info.html"]
    location = {
        "name": "Richard J Daley Center",
        "address": "50 W Washington St, LL 02 Chicago, IL 60602",
    }

    def parse(self, response):
        """Get all meeting schedule links (since years in URL aren't reliable)"""
        for link in response.css(".page-center .list-supporting-info a")[:10]:
            link_text = " ".join(link.css("*::text").extract())
            if "schedule" in link_text.lower():
                yield response.follow(
                    link.attrib["href"], callback=self._parse_meetings, dont_filter=True
                )

    def _parse_meetings(self, response):
        """
        `_parse_meetings` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        response_text = " ".join(
            response.css(".page-full-description *::text").extract()
        )
        self._validate_location(response_text)
        year_str = re.search(
            r"\d{4}", response.css("h1.page-heading::text").extract_first()
        ).group()
        time_str = (
            re.search(r"\d{1,2}:\d{2} [apm\.]{2,4}", response_text)
            .group()
            .replace(".", "")
        )

        for item in response.css(".page-full-description li"):
            item_text = " ".join(item.css("*::text").extract())
            meeting = Meeting(
                title="License Appeal Commission",
                description="",
                classification=COMMISSION,
                start=self._parse_start(item_text, time_str, year_str),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting, text=item_text)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item_text, time_str, year_str):
        """Parse start datetime as a naive datetime object."""
        date_str = re.sub(
            r"\s+", " ", re.search(r"[a-zA-Z]{3,10}\s+\d{1,2}", item_text).group()
        )
        return datetime.strptime(date_str + year_str + time_str, "%B %d%Y%I:%M %p")

    def _validate_location(self, response_text):
        """Check that location hasn't changed"""
        if "50 W" not in response_text:
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item, response):
        """
        Parse or generate links. No links are currently present, but it's similar to
        other pages where they are sometimes posted inside the li tag.
        """
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links
