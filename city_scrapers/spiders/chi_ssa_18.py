import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiSsa18Spider(CityScrapersSpider):
    name = "chi_ssa_18"
    agency = "Chicago Special Service Area #18 North Halsted"
    timezone = "America/Chicago"
    start_urls = ["https://northalsted.com/community/"]
    location = {
        "name": "Center on Halsted",
        "address": "3656 N Halsted St, Conference Room 200, Chicago IL 60613",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        table = response.xpath(
            '//*[@id="page_content_wrapper"]/div/div/div/div[1]/div[3]'
        )

        self._validate_location(table)
        self._validate_meeting_times(table)

        for item in table.xpath(".//h3 | .//p"):
            if "h3" in item.get():
                meeting_year = None
                meeting_year = item.xpath("descendant-or-self::text()").re_first(
                    r"\d{4}"
                )
                continue
            if "<p>" in item.get():
                split_items = [
                    Selector(text=section) for section in re.split(r"<br>", item.get())
                ]
                for split_string in split_items:
                    meeting_date_match = split_string.re_first(r"([A-Z]\w{2,}\s\d\d?)")
                    if not (meeting_date_match and meeting_year):
                        continue
                    converted_date = self._convert_date(
                        meeting_date_match, meeting_year
                    )

                    meeting = Meeting(
                        title="Commission",
                        description="",
                        classification=COMMISSION,
                        start=self._parse_start(converted_date),
                        end=self._parse_end(converted_date),
                        all_day=self._parse_all_day(item),
                        time_notes="",
                        location=self.location,
                        links=self._parse_links(split_string),
                        source=self._parse_source(response),
                    )

                    meeting["status"] = self._get_status(meeting)
                    meeting["id"] = self._get_id(meeting)

                    yield meeting

    def _validate_location(self, item):
        location_test = item.get()
        if "3656 N Halsted" not in location_test:
            raise ValueError("Meeting location has changed")
        elif "Conference Room 200" not in location_test:
            raise ValueError("Meeting location has changed")

    def _validate_meeting_times(self, item):
        meeting_time = item.get()
        if "9:00 am – 10:30 am" not in meeting_time:
            raise ValueError("Meeting time has changed")

    def _convert_date(self, meeting_date, meeting_year):
        split_date = meeting_date.split(" ")
        day = split_date[1]
        month = split_date[0]
        year = meeting_year
        converted_date = datetime.strptime(month + day + year, "%B%d%Y")
        return converted_date

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return item.replace(hour=9)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return item.replace(hour=10, minute=30)

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_links(self, item):
        """Parse or generate links."""
        parsed_links = []
        for links in item.xpath(".//a"):
            parsed_links.append(
                {
                    "href": links.xpath("@href").get(),
                    "title": links.xpath("text()").get(),
                }
            )
        return parsed_links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
