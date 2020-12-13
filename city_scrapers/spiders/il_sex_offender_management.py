from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.utils.response import open_in_browser
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import BytesIO, StringIO

import scrapy
import re



class IlSexOffenderManagementSpider(CityScrapersSpider):
    name = "il_sex_offender_management"
    agency = "Illinois Sex Offender Management Board"
    timezone = "America/Chicago"
    start_urls = ["https://www2.illinois.gov/idoc/Pages/SexOffenderManagementBoard.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        for link in response.css("#ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField a"):
            link_text = " ".join(link.css("*::text").extract())
            if "Meeting" not in link_text:
                continue
            if "Agenda" in link_text:
                yield scrapy.Request(
                    response.urljoin(link.attrib["href"]),
                    callback=self._parse_documents,
                    dont_filter=True,
                )

    def _parse_documents(self, response):
        """Parse meeting information from agenda PDF"""

        cleanText = self._cleanUpPDF(response)

        meeting = None
        # meeting = Meeting(
        #     title="SEX OFFENDER MANAGEMENT BOARD",
        #     description="N/A",
        #     classification=BOARD,
        #     status = self._parse_status,
        #     start= self._parse_start(response),
        #     end=self._parse_end(response),
        #     all_day=False,
        #     time_notes="See agenda to confirm details",
        #     location=self._parse_location(response),
        #     source=self.start_urls[0],
        # )

        yield meeting

    def _cleanUpPDF(self, response):
        """Clean up PDF and return text string"""
        import pdb; pdb.set_trace();

        lp = LAParams(line_margin=0.1)
        out_str = StringIO()
        extract_text_to_fp(BytesIO(response.body), out_str, laparams=lp)
        pdf_text = out_str.getvalue().replace("\n", "")
        # Remove duplicate characters not followed by lowercase (as in 5:00pm)
        clean_text = re.sub(r"([A-Z0-9:])\1(?![a-z])", r"\1", pdf_text, flags=re.M)
        # Remove duplicate spaces
        clean_text = re.sub(r"\s+", " ", clean_text)
        # year_str = re.search(r"\d{4}", clean_text).group()
        return clean_text

    def _parse_status(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
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
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }


    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
