import unicodedata
from datetime import datetime as dt

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlArtsCouncilSpider(CityScrapersSpider):
    name = "il_arts_council"
    agency = "Illinois Arts Council"
    timezone = "America/Chicago"
    start_urls = ["http://www.arts.illinois.gov/about-iac/governance/council-meetings"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for table in response.xpath("//table/tbody"):
            year = self._get_year(table)
            for item in table.xpath("./tr")[1::]:
                meeting = Meeting(
                    title=self._parse_title(item),
                    description=self._parse_description(item),
                    classification=self._parse_classification(item),
                    start=self._parse_start(item, year),
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item),
                    links=self._parse_links(item, response),
                    source=self._parse_source(response),
                )

                meeting_status = item.xpath("td[2]/text()").get() or ""
                meeting["status"] = self._get_status(meeting, text=meeting_status)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Agency Board"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object."""
        item_text = " ".join(item.css("td:first-child *::text").extract())
        text_clean = unicodedata.normalize("NFKD", item_text).strip()

        if text_clean[-4::] == year:
            start = dt.strptime(text_clean, "%A, %B %d, %Y")
        elif text_clean[-2::] in ["am", "pm"]:
            start = dt.strptime(text_clean + year, "%A, %B %d, %I:%M%p%Y")
        else:
            start = dt.strptime(text_clean + year, "%A, %B %d%Y")

        return start

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

        location = item.xpath("td[2]/text()").get()
        if not location:
            location = item.xpath("td[2]/a/text()").get()

        jrtc = {
            "address": "100 West Randolph, Suite 10-500, Chicago, IL 60601",
            "name": "IACA/JRTC",
        }

        tba = {
            "address": "TBA",
            "name": "TBA",
        }

        if "TBA" in location:
            return tba

        elif "JRTC" in location:
            return jrtc

        else:
            return {
                "address": "",
                "name": "",
            }

    def _parse_links(self, item, response):
        """Parse or generate links."""
        agenda_link = item.xpath("td/a/@href").get()
        if agenda_link:
            title = agenda_link.split("/")[-1].replace("%20", " ")
            if "www.arts.illinois.gov" not in agenda_link:
                agenda_link = response.urljoin(agenda_link)
            return [{"href": agenda_link, "title": title}]
        return []

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _get_year(self, item):
        """Gets the year for the meeting."""
        year_xpath = "../preceding-sibling::p/strong/text()"
        year_text = item.xpath(year_xpath)[-1].get()
        return year_text[0:4]
