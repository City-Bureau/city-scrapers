import re
from datetime import datetime
from io import BytesIO, StringIO

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


class CookEmergencyTelephoneSpider(CityScrapersSpider):
    name = "cook_emergency_telephone"
    agency = "Cook County Emergency Telephone System Board"
    timezone = "America/Chicago"
    start_urls = ["https://www.cookcounty911.com/"]
    location = {
        "name": "Conference Room",
        "address": "1401 S. Maybrook Drive, Maywood, IL 60153",
    }

    def __init__(self, *args, **kwargs):
        self.meeting_starts = []
        self.schedule_pdf_link = "/wp-content/uploads/pdfs/schedule.pdf"
        self.docs_link = ""
        self.agenda_link = ""
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        for link in response.css(".sliding_box a"):
            link_text = link.css("*::text").get()

            if "Minutes" in link_text:
                self.docs_link = link.attrib["href"]
            elif "Agenda" in link_text:
                self.agenda_link = link.attrib["href"]

        if not (self.docs_link == "" and self.agenda_link == ""):
            yield scrapy.Request(
                response.urljoin(self.schedule_pdf_link),
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
        lp = LAParams(line_margin=0.5)
        out_str = StringIO()
        extract_text_to_fp(BytesIO(response.body), out_str, laparams=lp)
        pdf_text = out_str.getvalue().replace("\n", "")

        # Remove duplicate characters not followed by lowercase (as in 5:00pm)
        clean_text = re.sub(r"([A-Z0-9:])\1(?![a-z])", r"\1", pdf_text, flags=re.M)

        # Remove duplicate spaces
        clean_text = re.sub(r"\s+", " ", clean_text)

        self._validate_location(clean_text)

        # Find dates in the format May 20, 2020 10:30 a.m
        DATE_PATTERN = (
            r"[a-zA-z]{3,9} [0-9]{2},\s[0-9]{4} [\d]{2}[:][\d]{2} (?:p[.]m|a[.]m)"
        )

        for date_str in re.findall(DATE_PATTERN, clean_text):
            self.meeting_starts.append(self._parse_start(date_str))

    def _parse_documents(self, response):
        """Parse agenda and minutes page"""
        for start in self.meeting_starts:
            meeting = Meeting(
                title="Cook County Emergency Telephone System Board",
                description=self._parse_description(),
                classification=BOARD,
                start=start,
                end=self._parse_end(start),
                all_day=False,
                time_notes="End time is estimated",
                location=self.location,
                links=self._parse_links(response, start),
                source=self.start_urls[0],
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_description(self):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, date_str):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(date_str.replace(".", ""), "%B %d, %Y %H:%M %p")

    def _parse_end(self, start):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_links(self, response, start):
        """Parse agendas and minutes."""

        minutes_href = ""

        for link in response.css(".minuteYearBlock a"):
            link_text = link.css("*::text").get()

            if link_text == start.strftime("%m-%Y"):
                minutes_href = response.urljoin(link.attrib["href"])
                break

        links_map = []

        if not minutes_href == "":
            links_map.append({"title": "Minutes", "href": minutes_href})

        agenda_href = response.urljoin(self.agenda_link)

        links_map.append(
            {
                "title": "Agenda",
                "href": "{}?date={}".format(agenda_href, start.strftime("%Y%m%d")),
            }
        )

        return links_map

    def _validate_location(self, text):
        if "Maywood" not in text:
            raise ValueError("Meeting location has changed")
