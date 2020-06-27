import re
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from PyPDF2 import PdfFileReader


class ChiHumanRelationsSpider(CityScrapersSpider):
    name = "chi_human_relations"
    agency = "Chicago Commission on Human Relations"
    timezone = "America/Chicago"
    start_urls = ["https://www.chicago.gov/city/en/depts/cchr.html"]
    location = {
        "name": "",
        "address": "740 N Sedgwick St, 4th Floor Boardroom, Chicago, IL 60654",
    }

    def __init__(self, *args, **kwargs):
        self.meeting_starts = []
        self.docs_link = ""
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        schedule_link = ""
        for link in response.css(".related-links a"):
            link_text = " ".join(link.css("*::text").extract())
            if "Board" in link_text and "Schedule" in link_text:
                schedule_link = link.attrib["href"]
            elif "Minutes" in link_text:
                self.docs_link = link.attrib["href"]
        if schedule_link and self.docs_link:
            yield scrapy.Request(
                response.urljoin(schedule_link),
                callback=self._parse_schedule,
                dont_filter=True,
            )
        else:
            raise ValueError("Required links not found")

    def _parse_schedule(self, response):
        """Parse PDF and then yield to documents page"""
        self._parse_schedule_pdf(response)
        yield scrapy.Request(
            response.urljoin(self.docs_link),
            callback=self._parse_documents,
            dont_filter=True,
        )

    def _parse_schedule_pdf(self, response):
        """Parse dates and details from schedule PDF"""
        pdf_obj = PdfFileReader(BytesIO(response.body))
        pdf_text = pdf_obj.getPage(0).extractText().replace("\n", "")
        # Remove duplicate characters not followed by lowercase (as in 5:00pm)
        clean_text = re.sub(r"([A-Z0-9:])\1(?![a-z])", r"\1", pdf_text, flags=re.M)
        # Remove duplicate spaces
        clean_text = re.sub(r"\s+", " ", clean_text)
        year_str = re.search(r"\d{4}", clean_text).group()
        self._validate_location(clean_text)

        for date_str in re.findall(r"[A-Z]{3,10}\s+\d{1,2}(?!\d)", clean_text):
            self.meeting_starts.append(self._parse_start(date_str, year_str))

    def _parse_documents(self, response):
        """Parse agenda and minutes page"""
        link_map = self._parse_link_map(response)
        for start in self.meeting_starts:
            meeting = Meeting(
                title="Board of Commissioners",
                description="",
                classification=COMMISSION,
                start=start,
                end=self._parse_end(start),
                all_day=False,
                time_notes="See agenda to confirm details",
                location=self.location,
                links=link_map[(start.month, start.year)],
                source=self.start_urls[0],
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, date_str, year_str):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(
            "{} {} 15:30".format(date_str, year_str), "%B %d %Y %H:%M"
        )

    def _parse_end(self, start):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return start + timedelta(hours=1, minutes=30)

    def _parse_link_map(self, response):
        """
        Parse or generate links. Returns a dictionary of month, year tuples and link
        lists
        """
        link_map = defaultdict(list)
        for link in response.css(".page-full-description-above a"):
            link_text = " ".join(link.css("*::text").extract()).strip()
            link_date_match = re.search(r"[A-Z][a-z]{2,9} \d{4}", link_text)
            if not link_date_match:
                continue
            link_date_str = link_date_match.group()
            link_start = datetime.strptime(link_date_str, "%B %Y")
            link_map[(link_start.month, link_start.year)].append(
                {
                    "title": "Agenda" if "Agenda" in link.attrib["href"] else "Minutes",
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return link_map

    def _validate_location(self, text):
        if "740" not in text:
            raise ValueError("Meeting location has changed")
