import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa48Spider(CityScrapersSpider):
    name = "chi_ssa_48"
    agency = "Chicago Special Service Area #48 Old Town"
    timezone = "America/Chicago"
    start_urls = ["https://oldtownchicago.org/ssa-48/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting_year = response.xpath("//div[@class='meeting-dates-block']/h2")
        meeting_date = response.xpath("//div[@class='meeting-dates-block']/h5")
        meeting_info = response.xpath("//div[@class='meeting-dates-block']/p")
        meeting_links = response.xpath("//div[@class='meeting-minutes-block']")

        for item_date, item_info in zip(meeting_date, meeting_info):

            start_time, end_time = self._parse_start_end(
                item_date, item_info, meeting_year
            )

            meeting = Meeting(
                title="Commission",
                description="",
                classification=COMMISSION,
                start=start_time,
                end=end_time,
                all_day=False,
                time_notes="",
                location=self._parse_location(item_info),
                links=self._parse_links(start_time, meeting_links),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(
                meeting, text=meeting_info.xpath(".//text()").get()
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start_end(self, date, info, year):
        meeting_year = year.xpath("//div[@class='meeting-dates-block']/h2/text()").get()
        parse_year = meeting_year.split(" ")
        year = parse_year[0]

        meeting_date = date.xpath(".//text()").get()
        meeting_time = info.xpath(".//text()").get()
        parse_time = meeting_time.split("-")

        start_time = datetime.strptime(
            year + " " + meeting_date + " " + parse_time[0] + " " + parse_time[1][-2:],
            "%Y %A %B %d %I:%M %p",
        )

        end_time = datetime.strptime(
            year + " " + meeting_date + " " + parse_time[1], "%Y %A %B %d %I:%M%p"
        )

        return start_time, end_time

    def _parse_location(self, info):
        """Parse or generate location."""
        element = info.xpath(".//text()").getall()

        name = re.sub(r"\s+", " ", element[1]).strip()
        """If the location is not known, the element contains only two strings """
        if len(element) > 2:
            address = re.sub(r"[\(\)]", "", re.sub(r"\s+", " ", element[2]).strip())
        else:
            address = name
        if "TBD" not in address and "Chicago" not in address:
            address += " Chicago, IL"

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, start_time, meeting_links):
        """Parse or generate links."""
        links = []
        for href in meeting_links.xpath(".//a"):
            title = href.xpath("text()").get().strip()
            minutes_date = title.split(" ")
            # Verification, that selected link is a link to meeting minutes
            if len(minutes_date) >= 2 and minutes_date[1] != "Minutes":
                continue
            # Date format for the last meeting minutes uses 2019 instead of 19 format
            if minutes_date[2][-3] != "/":
                meeting_minutes_date = datetime.strptime(minutes_date[2], "%m/%d/%Y")
            else:
                meeting_minutes_date = datetime.strptime(minutes_date[2], "%m/%d/%y")

            if meeting_minutes_date.date() == start_time.date():
                links.append(
                    {"title": title, "href": href.xpath("@href").get().strip()}
                )

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
