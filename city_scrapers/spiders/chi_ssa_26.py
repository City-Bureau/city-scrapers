import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa26Spider(CityScrapersSpider):
    name = "chi_ssa_26"
    agency = "Chicago Special Service Area #26 Broadway Commercial District"
    timezone = "America/Chicago"
    start_urls = ["https://www.edgewater.org/ssa-26/commissionmeetings/"]
    location = {
        "name": "Edgewater Chamber of Commerce",
        "address": "1210 W Rosedale Ave Chicago, IL 60660",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self.link_map = {}
        self._parse_links(response)
        self._parse_upcoming(response)

        for start, links in self.link_map.items():
            meeting = Meeting(
                title="Commission",
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=links,
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_links(self, response):
        """Parse or generate links."""
        for link in response.css("p a"):
            # Standardize whitespace characters
            link_text = re.sub(r"[\s\t\r]+", " ", link.css("*::text").extract_first())
            dt_match = re.search(
                r"[a-z]+ \d{1,2}, \d{4},? at [\d:o]{4,5} ?[apm\.]{2,4}",
                link_text,
                flags=re.I,
            )
            if not dt_match:
                continue
            dt_str = dt_match.group()
            # Cleanup formatting, removing inconsistent punctuation
            dt = datetime.strptime(
                re.sub(r"([\.,]| (?=[pa][\.m]))", "", dt_str.replace("oo", "00")),
                "%B %d %Y at %I:%M%p",
            )
            self.link_map[dt] = [{"title": "Minutes", "href": link.attrib["href"]}]

    def _parse_upcoming(self, response):
        """Parse upcoming meetings"""
        for section in response.css("p"):
            section_label = section.css("strong:first-child::text").extract_first()
            if not (section_label and section_label.strip().startswith("20")):
                continue
            year_str = section_label.strip()
            meetings = section.xpath("./text()").extract()
            for meeting in meetings:
                meeting_dt_match = re.search(
                    r"[a-z]{3,9} \d{1,2} at [\d:apm\.]{4,8}", meeting, flags=re.I
                )
                if not meeting_dt_match:
                    continue
                # Change 3:pm to 3:00pm
                meeting_dt_str = re.sub(r":(?=[ap])", ":00", meeting_dt_match.group())
                meeting_dt = datetime.strptime(
                    "{} {}".format(year_str, meeting_dt_str), "%Y %B %d at %I:%M%p"
                )
                if meeting_dt not in self.link_map:
                    self.link_map[meeting_dt] = []
