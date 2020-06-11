import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookLocalRecordsSpider(CityScrapersSpider):
    name = "cook_local_records"
    agency = "Cook County Local Records Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://cyberdriveillinois.com/departments/archives/records_management/lrc_cook_county_meeting_schedule.html"  # noqa
    ]
    location = {
        "name": "James R Thompson Center",
        "address": "100 W Randolph St, Room 9-035 Chicago, IL 60601",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        description = response.css(".content > p::text").extract_first()
        if not re.search(r"100 W(est)? Randolph", description):
            raise ValueError("Meeting location has changed")
        for item in response.css(".content > ul li"):
            meeting = Meeting(
                title="Local Records Commission",
                description="",
                classification=COMMISSION,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(
                meeting, text=" ".join(item.css("*::text").extract())
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        day_str = item.xpath("./text()").extract_first()
        date_str = re.search(r"\w+\s+\d{1,2},\s+\d{4}", day_str).group()
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        return datetime.combine(date_obj.date(), time(11))

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": link.xpath("./text()").extract_first().strip(),
                    "href": response.urljoin(link.xpath("@href").extract_first()),
                }
            )
        return links
