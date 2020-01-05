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

        for item_date, item_info in zip(meeting_date, meeting_info):
            meeting = Meeting(
                title="Special Service Area 48 Meeting",
                description="",
                classification=COMMISSION,
                start=self._parse_start(item_date, item_info, meeting_year),
                end=self._parse_end(item_date, item_info, meeting_year),
                all_day=False,
                time_notes="",
                location=self._parse_location(item_info),
                links=[],
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting, meeting_info.xpath(".//text()").get())
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, date, info, year):
        meeting_year = year.xpath("//div[@class='meeting-dates-block']/h2/text()").get()
        parse_year = meeting_year.split(" ")
        year = parse_year[0]

        meeting_date = date.xpath(".//text()").get()
        meeting_time = info.xpath(".//text()").get()
        parse_time = meeting_time.split("-")

        start_time = datetime.strptime(
            year + " " + meeting_date + " " + parse_time[0] + " " + parse_time[1][-2:],
            "%Y %A %B %d %I:%M %p"
        )

        return start_time

    def _parse_end(self, date, info, year):
        meeting_year = year.xpath("//div[@class='meeting-dates-block']/h2/text()").get()
        parse_year = meeting_year.split(" ")
        year = parse_year[0]

        meeting_date = date.xpath(".//text()").get()
        meeting_time = info.xpath(".//text()").get()
        parse_time = meeting_time.split("-")
        print(parse_time[1])

        end_time = datetime.strptime(
            year + " " + meeting_date + " " + parse_time[1], "%Y %A %B %d %I:%M%p"
        )

        return end_time

    def _parse_location(self, info):
        """Parse or generate location."""
        element = info.xpath(".//text()").getall()
        index = element[1].rfind("/n/t/t")
        name = element[1][index + 1:].strip()

        index = element[2].rfind("/r/n")
        address = element[2][index + 1:].strip()

        return {
            "address": address,
            "name": name,
        }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
