import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiPoliceBoardSpider(CityScrapersSpider):
    name = "chi_policeboard"
    timezone = "America/Chicago"
    agency = "Chicago Police Board"
    start_urls = ["https://chicago.gov/city/en/depts/cpb/provdrs/public_meetings.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        year = self._parse_year(response)
        location = self._parse_location(response)
        start_time = self._parse_start_time(response)

        for item in response.xpath('//p[contains(@style,"padding-left")]'):
            start_date = self._parse_start_date(item, year)
            if not start_date:
                continue
            meeting = Meeting(
                title="Police Board",
                description="",
                classification=BOARD,
                start=datetime.combine(start_date, start_time),
                end=None,
                time_notes="",
                all_day=False,
                location=location,
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting)
            yield meeting

    def _parse_links(self, item, response):
        anchors = item.xpath("a")
        return [
            {
                "href": response.urljoin(link.xpath("@href").extract_first("")),
                "title": link.xpath("text()").extract_first(""),
            }
            for link in anchors
        ]

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        loc_text = " ".join(response.xpath("//strong/text()").extract())
        if "3510 South" not in loc_text:
            raise ValueError("Meeting location has changed")
        return {
            "address": "3510 S Michigan Ave, Chicago IL 60653",
            "name": "Chicago Public Safety Headquarters",
        }

    def _parse_start_time(self, response):
        """
        Return start time
        """
        bold_text = " ".join(response.xpath("//strong/text()").extract())
        match = re.match(r".*(\d+:\d\d\s*[p|a]\.*m\.*).*", bold_text.lower())
        if match:
            cleaned_time = match.group(1).replace(" ", "").replace(".", "").upper()
            return datetime.strptime(cleaned_time, "%I:%M%p").time()
        return None

    def _parse_start_date(self, item, year):
        """
        Parse start date
        """
        date_str = item.css("::text").extract_first()
        clean_date_match = re.search(r"[A-Za-z]+\s+\d{1,2}", date_str)
        if not clean_date_match:
            return None
        date_with_year = "{0}, {1}".format(clean_date_match.group(), year)
        return datetime.strptime(date_with_year, "%B %d, %Y").date()

    def _parse_year(self, response):
        """
        Look for a string of 4 numbers to be the year.
        If not found, use current year.
        """
        for entry in response.xpath("//h3/text()").extract():
            year_match = re.search(r"([0-9]{4})", entry)
            if year_match:
                return year_match.group(1)
