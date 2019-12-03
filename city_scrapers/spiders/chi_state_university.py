from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiStateUniversitySpider(CityScrapersSpider):
    name = "chi_state_university"
    agency = "Chicago State University"
    timezone = "America/Chicago"
    start_urls = ["https://www.csu.edu/boardoftrustees/dates.htm"]

    def parse(self, response):
        for item in response.css(".table tr td li"):
            extracted = item.css("::text").extract()
            meeting = Meeting(
                title=self._parse_title(response),
                classification=self._parse_classification(),
                start=self._parse_start(extracted),
                end=self._parse_end(extracted),
                all_day=self._parse_all_day(extracted),
                time_notes=self._parse_time_notes(extracted),
                location=self._parse_location(),
                source=self._parse_source(response),
            )

            if "RESCHEDULED" in extracted:
                meeting["status"] = self._get_status(meeting, text="Meeting is Rescheduled")
            else:
                meeting["status"] = self._get_status(meeting, text="Meeting is Confirmed")
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, response):
        title = response.css(".goldenTitle::text").extract_first()
        return title

    def _parse_classification(self):
        return BOARD

    def _parse_start(self, item):
        wrong_char = "\xa0"
        time = item[0].replace(wrong_char, '').strip()
        date = None
        try:
            date = datetime.strptime(time, "%A, %B %d, %Y")
        except Exception:
            print("Can't get a date")
            date = datetime.now()
        return date

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        notes = ""
        if "RESCHEDULED" in item:
            notes = "Rescheduled to {}".format(item.pop())
        return notes

    def _parse_all_day(self, item):
        return False

    def _parse_location(self):
        return {
            "address": "Room 415",
            "name": "Gwendolyn Brooks Library Auditorium",
        }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
