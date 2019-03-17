import datetime
import re

from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.constants import ADVISORY_COMMITTEE


class CookMedicalExaminerSpider(CityScrapersSpider):
    name = "cook_medical_examiner"
    agency = "Cook County Medical Examiner's Advisory Committee"
    timezone = "America/Chicago"
    allowed_domains = ["www.cookcountyil.gov"]
    start_urls = ["https://www.cookcountyil.gov/service/medical-examiners-advisory-committee"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meetings = response.css(".field-items strong *::text").getall()
        dates = []
        for i, item in enumerate(meetings):
            if "Time" in item:
                times = re.findall("(1[0-2]|0?[1-9]):([0-5]\\d)\\s*([AaPp][Mm])", item)
                start_time = times[0]
                end_time = times[1]
            if "Location" in item:
                venue = item.split(": ")[1]
                street = meetings[i + 1] + "; " + meetings[i + 2]
                address = {"name": venue, "address": street.replace(u'\xa0', u' ')}
            if re.match(
                "((Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day), "
                "((Jan|Febr)uary|March|April|May|June|July|August|"
                "(Septem|Octo|Novem|Decem)ber) "
                "[1-3]*\\d, "
                "\\d{4}", item
            ):
                dates.append(item)

        for i, d in enumerate(dates):
            meeting = Meeting(
                title=self._parse_title(response),
                description=self._parse_description(i, response),
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(d, start_time),
                end=self._parse_end(d, end_time),
                all_day=False,
                location=address,
                links=self._parse_links(d),
                source=self._parse_source(response),
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, response):
        return response.css("#page-title *::text").get().strip().replace("\\", "")

    def _parse_description(self, i, response):
        """Parse or generate meeting description."""
        if i == 0:
            # We only have the agenda for the first meeting.
            agenda = response.css("li:not([class*='leaf']) *::text").getall()
            return "\n".join([a.strip().replace("\\", "") for a in agenda if a != ''])
        else:
            return ""

    def _parse_start(self, date, start_time):
        """Parse start datetime as a naive datetime object."""
        if "Date" in date:
            return
        dt = datetime.datetime.strptime(date + str(start_time), "%A, %B %d, %Y('%I', '%M', '%p')")
        return dt

    def _parse_end(self, date, end_time):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        if "Date" in date:
            return
        dt = datetime.datetime.strptime(date + str(end_time), "%A, %B %d, %Y('%I', '%M', '%p')")
        return dt

    def _parse_links(self, item):
        """Parse or generate links."""
        return []

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
