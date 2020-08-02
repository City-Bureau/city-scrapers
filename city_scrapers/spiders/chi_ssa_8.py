import datetime
import re
import unicodedata
from calendar import day_name, month_name

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from w3lib.html import remove_tags


class ChiSsa8Spider(CityScrapersSpider):
    name = "chi_ssa_8"
    agency = "Chicago Special Service Area #8 Lakeview East"
    timezone = "America/Chicago"
    start_urls = ["https://lakevieweast.com/ssa-8/"]

    months = {m.lower() for m in month_name[1:]}
    days = {d.lower() for d in day_name[1:]}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".post-content ul"):
            bodyText = item.extract()
            if "Location" in bodyText:
                year = self._parse_year(item)
                if year is not None:
                    location = self._parse_location(item)
                    for li in item.css("li"):
                        startDate = self._parse_start(li, year)
                        if startDate is not None:
                            meeting = Meeting(
                                title=self._parse_title_desc(li),
                                description=self._parse_title_desc(li),
                                classification=self._parse_classification(li),
                                start=startDate,
                                end=self._parse_end(li),
                                all_day=self._parse_all_day(li),
                                time_notes=self._parse_time_notes(li),
                                location=location,
                                links=self._parse_links(li),
                                source=self._parse_source(response),
                            )
                            meeting["status"] = self._get_status(meeting)
                            meeting["id"] = self._get_id(meeting)

                            yield meeting

    def _parse_year(self, item):
        header = item.xpath("./preceding::h3[1]")
        if header[0].extract():
            headerString = header[0].extract()
            if re.search("[1-3][0-9]{3}", headerString):
                return re.search("[1-3][0-9]{3}", headerString).group()
            return None

    def _parse_title_desc(self, item):
        raw = remove_tags(item.extract())
        title = " ".join([s.replace(",", "") for s in raw.split(" ")][3:])
        rmStrings = ["-", "(", ")"]
        for x in rmStrings:
            title = title.replace(x, "")
        title = title.replace("–", "")
        return unicodedata.normalize("NFKD", title.strip())

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item, year):
        raw = remove_tags(item.extract())
        dateString = [s.replace(",", "") for s in raw.split(" ")][:3]
        if dateString[0] in day_name and dateString[1] in month_name:
            dateString.append(year)
            return datetime.datetime.strptime(" ".join(dateString[:4]), "%A %B %d %Y")
        return None

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
        locationString = (
            item.xpath("//li[contains(text(), 'Location')]").extract_first().strip()
        )
        locationString = remove_tags(locationString)
        rmStrings = ["Location", ":"]
        for x in rmStrings:
            locationString = locationString.replace(x, "")
        return {
            "address": locationString.strip(),
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
