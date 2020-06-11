import re
from datetime import datetime, time

from city_scrapers_core.constants import ADVISORY_COMMITTEE, CANCELLED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookMedicalExaminerSpider(CityScrapersSpider):
    name = "cook_medical_examiner"
    agency = "Cook County Medical Examiner's Advisory Committee"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.cookcountyil.gov/service/medical-examiners-advisory-committee"
    ]
    location = {
        "name": "Office of the Medical Examiner",
        "address": "2121 W Harrison St, Chicago, IL 60612",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        cancel_date = None
        for header in response.css(".field-items h2::text, .field-items h3::text"):
            header_text = header.extract()
            if header_text and "cancel" in header_text.lower():
                cancel_date = self._parse_date(header_text)

        # Parse default start and end time from description text
        default_start_time, default_end_time = self._parse_times(
            " ".join(response.css(".field-items p:not([align])::text").extract())
        )
        for date_item in response.css(".field-items p[align='center']"):
            date_str = " ".join(date_item.css("*::text").extract())
            date_obj = self._parse_date(date_str)
            if not date_obj:
                continue
            start_time, end_time = self._parse_times(date_str)
            meeting = Meeting(
                title="Medical Examiner's Advisory Committee",
                description="",
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(date_obj, start_time or default_start_time),
                end=self._parse_end(date_obj, end_time or default_end_time),
                time_notes="",
                all_day=False,
                location=self.location,
                links=[],
                source=response.url,
            )
            meeting["status"] = self._parse_status(
                meeting, date_str, date_obj, cancel_date
            )
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_date(self, date_str):
        """Parse date string from common format"""
        date_match = re.search(r"[a-zA-Z]{3,10} \d{1,2},? \d{4}", date_str)
        if not date_match:
            return
        return datetime.strptime(date_match.group().replace(",", ""), "%B %d %Y").date()

    def _parse_times(self, text):
        time_strs = re.findall(r"(\d{1,2}(\:\d{2})? ?[apm\.]{2,4})", text, flags=re.I)
        start_time = None
        end_time = None
        if len(time_strs) > 0:
            start_time_str = re.sub(r"[\s\.]", "", time_strs[0][0])
            if ":" not in start_time_str:
                start_time_str = re.sub(
                    r"(\d+)([apm\.])", r"\1:00\2", start_time_str, flags=re.I
                )
            start_time = datetime.strptime(start_time_str, "%I:%M%p").time()
        if len(time_strs) > 1:
            end_time_str = re.sub(r"[\s\.]", "", time_strs[1][0])
            if ":" not in end_time_str:
                end_time_str = re.sub(
                    r"(\d+)([apm\.])", r"\1:00\2", end_time_str, flags=re.I
                )
            end_time = datetime.strptime(end_time_str, "%I:%M%p").time()
        return start_time or time(11), end_time

    def _parse_start(self, date_obj, start_time):
        """Parse start datetime as a naive datetime object."""
        return datetime.combine(date_obj, start_time)

    def _parse_end(self, date_obj, end_time):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        # Dont return an end time if the end time object is None
        if end_time is None:
            return
        return datetime.combine(date_obj, end_time)

    def _parse_status(self, item, date_str, date_obj, cancel_date):
        if date_obj == cancel_date:
            return CANCELLED
        return self._get_status(item, text=date_str)

    def _validate_location(self, response):
        response_text = " ".join(response.css("*::text").extract())
        if "2121 W" not in response_text:
            raise ValueError("Meeting location has changed")
