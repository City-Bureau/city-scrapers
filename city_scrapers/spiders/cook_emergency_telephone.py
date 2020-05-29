import re
from datetime import datetime, timedelta
from io import BytesIO

import scrapy
from city_scrapers_core.constants import FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from PyPDF2 import PdfFileReader


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
        self.docs_link = ""
        self.agenda_link = ""
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        schedule_link = ""
        for link in response.css(".sliding_box a"):
            link_text = link.css("*::text").get()

            schedule_link = self.start_urls[0] + '/wp-content/uploads/pdfs/'

            if "Minutes" in link_text:
                self.docs_link = link.attrib["href"]
            elif "Agenda" in link_text:
                self.agenda_link = link.attrib["href"]

        if schedule_link and self.docs_link:
            yield scrapy.Request(
                response.urljoin(schedule_link), callback=self._parse_schedule, dont_filter=True
            )
        else:
            raise ValueError("Required links not found")

    def _parse_schedule(self, response):
        """Parse PDF and then yield to documents page"""
        schedule_pdf_link = 'schedule.pdf'

        yield scrapy.Request(
            response.urljoin(schedule_pdf_link),
            callback=self._parse_schedule_pdf,
            dont_filter=True
        )

        yield scrapy.Request(
            response.urljoin(self.docs_link), callback=self._parse_documents, dont_filter=True
        )

    def _parse_schedule_pdf(self, response):
        """Parse dates and details from schedule PDF"""
        pdf_obj = PdfFileReader(BytesIO(response.body))
        pdf_text = pdf_obj.getPage(0).extractText().replace("\n", "")

        # Remove duplicate characters not followed by lowercase (as in 5:00pm)
        clean_text = re.sub(r"([A-Z0-9:])\1(?![a-z])", r"\1", pdf_text, flags=re.M)

        # Remove duplicate spaces
        clean_text = re.sub(r"\s+", " ", clean_text)

        self._validate_location(clean_text)

        # Find dates in the format May 20, 2020 10:30 a.m
        DATE_PATTERN = r"[a-zA-z]{3,9} [0-9]{2},\s[0-9]{4} [\d]{2}[:][\d]{2} (?:p[.]m|a[.]m)"

        for date_str in re.findall(DATE_PATTERN, clean_text):
            self.meeting_starts.append(self._parse_start(date_str))

    def _parse_documents(self, response):
        """Parse agenda and minutes page"""
        for start in self.meeting_starts:
            meeting = Meeting(
                title="Cook County Emergency Telephone System Board Public Meeting",
                description=self._parse_description(),
                classification=FORUM,
                start=start,
                end=self._parse_end(start),
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(response),
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
        return FORUM

    def _parse_start(self, date_str):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(date_str.replace('.', ''), "%B %d, %Y %H:%M %p")

    def _parse_end(self, start):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return start + timedelta(hours=1, minutes=30)

    def _parse_links(self, response):
        """Parse or generate links."""
        return [{
            "title": "Minutes",
            "href": response.urljoin(self.docs_link)
        }, {
            "title": "Agenda",
            "href": response.urljoin(self.agenda_link)
        }]

    def _validate_location(self, text):
        if "Maywood" not in text:
            raise ValueError("Meeting location has changed")
