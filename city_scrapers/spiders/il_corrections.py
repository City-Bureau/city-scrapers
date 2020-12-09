from io import BytesIO, StringIO
from datetime import datetime, timedelta

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


class IlCorrectionsSpider(CityScrapersSpider):
    name = "il_corrections"
    agency = "Illinois Department of Corrections Advisory Board"
    timezone = "America/Chicago"
    start_urls = ["https://www2.illinois.gov/idoc/aboutus/advisoryboard/Pages/default.aspx"]

    def __init__(self):
        self.links = {}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Gather Meeting Dates/Links
        self.links = self._parse_all_links(response)
        

          # Parse 1 document - ideally Agenda
          # get start/end time (re), combine with date
          # Title - switch on existence of subcomittee
          # Location
          # source = response.url

        meeting = Meeting(
            title=self._parse_title(item),
            description="",
            classification=self._parse_classification(item),
            start=self._parse_start(item),
            end=self._parse_end(item),
            all_day=False,
            time_notes="",
            location=self._parse_location(item),
            links=self._parse_links(item),
            source=self._parse_source(response),
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting


    def _parse_pdf(self, item):
        """Parse dates and details from schedule PDF"""
        lp = LAParams(line_margin=0.1)
        out_str = StringIO()
        extract_text_to_fp(BytesIO(response.body), out_str, laparams=lp)
        pdf_text = out_str.getvalue().replace("\n", "")

        return pdf_text

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

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
    def _parse_all_links(self, response):
        """ Gather dates, links """
        for link in response.css('a'):
            date = link.re_first("""((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|
            May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|
            Dec(ember)?)\s+\d{1,2},\s+\d{4})|((1[0-2]|0?[1-9])/(3[01]|
            [12][0-9]|0?[1-9])/(?:[0-9]{2})?[0-9]{2})""")

            if date is not None:
                if date not in self.links.keys():
                    self.links[date] = []
                for item in ["Notice", "Agenda", "Minutes"]:
                    if item in link.attrib['href']:
                        self.links[date].append({"title": item,
                                                 "href": link.attrib['href']})
    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
