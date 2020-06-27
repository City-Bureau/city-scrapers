import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlBoardOfExaminersSpider(CityScrapersSpider):
    name = "il_board_of_examiners"
    agency = "Illinois Board of Examiners"
    timezone = "America/Chicago"
    start_urls = ["https://www.ilboe.org/board-information/board-meetings/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for item in response.css(".minutes"):
            start = self._parse_start(item)
            if start < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE"):
                continue
            meeting = Meeting(
                title="Illinois Board of Examiners",
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_str = re.sub(r"(?<=\d)[a-z]+", "", item.css(".minuteDate::text").get())
        time_str = item.css(".minuteTime::text").get()
        datetimeObj = ""
        datetimeObj = datetime.strptime(date_str + ":" + time_str, "%B %d, %Y:%I:%M %p")
        return datetimeObj

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
        temp_address = item.css(".minuteLocation p::text").extract()
        [name, address] = ["", ""]
        if temp_address:
            if temp_address[0][0].isdigit():
                name = ""
                address = self.remove_special_chars("".join(temp_address))
            else:
                [name, address] = "".join(temp_address).split("\n", 1)
                name = self.remove_special_chars(name)
                address = self.remove_special_chars(address)
        return {
            "name": name,
            "address": address,
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        agenda_link = item.css(".minuteAgenda").css("a::attr(href)").get()
        mom_link = item.css(".minuteMinutes").css("a::attr(href)").get()
        links = []
        if agenda_link:
            links.append({"href": agenda_link, "title": "Agenda"})
        if mom_link:
            links.append({"href": mom_link, "title": "Minutes"})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def remove_special_chars(self, string_val):
        """Remove all special chars from string"""
        return re.sub(r"\s+", " ", string_val.replace("\n", ", ")).strip()
