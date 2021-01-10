from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa31Spider(CityScrapersSpider):
    name = "chi_ssa_31"
    agency = "Chicago Special Service Area"
    timezone = "America/Chicago"
    start_urls = ["http://ravenswoodchicago.org/ssa-31-commission-meetings/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        inner_block = response.css("div.wp-block-group__inner-container")
        time_notes = response.css("em::text")[-1].get()
        meetings = inner_block[1].css("li")

        for item in meetings:
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=time_notes,
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return " ".join(item.css("::text")[2].get().split()[1:])

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_item = item.css("::text")[0].get()
        date_item = " ".join(date_item.split()[:-1])
        date_item = date_item.replace("at ", "").replace(".", "")
        date_item += f" {datetime.today().year}"

        date_obj = datetime.strptime(date_item, "%B %d %I:%M %p %Y")
        return date_obj

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "Confirm with agency",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [
            {
                "href": item.css("a::attr(href)").get(),
                "title": item.css("::text")[1].get(),
            }
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
