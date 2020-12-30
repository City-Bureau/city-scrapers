import re
import scrapy

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
        self.url_base = "https://www2.illinois.gov"
        self.pdf_text = ""

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Gather Meeting Dates/Links
        self.links = self._parse_all_links(response)

        for date in self.links.keys():
            if "Agenda" in self.links[date].keys():
                yield scrapy.Request(
                    self.links[date]["Agenda"],
                    callback=self._meeting,
                    cb_kwargs=dict(date=date)
                )
            elif "Minutes" in self.links[date].keys():
                yield scrapy.Request(
                    self.links[date]["Minutes"],
                    callback=self._meeting,
                    cb_kwargs=dict(date=date)
                )

    def _meeting(self, response, date):
        print("meeting")
        self.pdf_text = self._parse_pdf(response)
        meeting = Meeting(
            title=self._parse_title(),
            description="",
            classification="ADVISORY_COMMITTEE",
            start=self._parse_times(date),
            end=self._parse_times(date, False),
            all_day=False,
            time_notes="",
            location=self._parse_location(),
            links=self._parse_links(date),
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting


    def _parse_pdf(self, response):
        """Parse dates and details from schedule PDF"""
        print("prase pdf)")
        lp = LAParams(line_margin=0.1)
        out_str = StringIO()
        extract_text_to_fp(BytesIO(response.body), out_str, laparams=lp)
        pdf_text = out_str.getvalue()
        return pdf_text.lower()

    def _parse_title(self):
        """Parse or generate meeting title."""
        title = "Adult Advisory Board Meeting"

        if "subcommittee" in self.pdf_text:
            title = "Adult Advisory Board / Women's Subcommittee Meeting"
        return title

    def _parse_times(self, date, start=True):
        """Parse start datetime as a naive datetime object."""
        times = re.findall("(\d{1,2}:\d{2} ?(am|a\.m\.|pm|p\.m\.))", self.pdf_text.lower())
        start_time = times[0][0].replace(".", "")
        end_time = times[1][0].replace(".", "")

        # Add conversion to datetime object
        if start:
            return self._try_time_format(date, start_time)
        else:
            return self._try_time_format(date, end_time)

        return time

    def _try_time_format(self, date, time):
        """Try time formatting with and without spacing"""
        try:
            time_object = datetime.strptime(f"{date} {time}", "%B %d, %Y %I:%M%p")
        except ValueError:
            time_object = datetime.strptime(f"{date} {time}", "%B %d, %Y %I:%M %p")

        return time_object

    def _parse_location(self):
        """Parse or generate location."""

        location_lookup = {
            "logan correctional center": {
                "address": "1096 1350th St, Lincoln, IL 62656",
                "name": "Logan Correctional Center"
            },
            "vandalia correctional center": {
                "address": "US-51, Vandalia, IL 62471",
                "name": "Vandalia Correctional Center"
            },
            "thompson center": {
                "address": "100 W. Randolph, Suite 4-200, Chicago, IL 60601",
                "name": "James R. Thompson Center"
            },
            "joliet treatment center": {
                "address": "2848 McDonough St, Joliet, IL 60431",
                "name": "Joliet Treatment Center"
            }
        }

        for location in location_lookup.keys():
            if location in self.pdf_text:
                return location_lookup[location]

    def _parse_all_links(self, response):
        """ Gather dates, links """
        for link in response.css('a'):
            date = link.re_first("""((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|
            May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|
            Dec(ember)?)\s+\d{1,2},\s+\d{4})|((1[0-2]|0?[1-9])/(3[01]|
            [12][0-9]|0?[1-9])/(?:[0-9]{2})?[0-9]{2})""")

            if date is not None:
                if date not in self.links:
                    self.links[date] = {}
                for item in ["Notice", "Agenda", "Minutes"]:
                    if item in link.attrib['href']:
                        self.links[date][item] = self.url_base + link.attrib['href']

        return self.links

    def _parse_links(self, date):
        """Parse or generate links."""
        link_list = []
        for key, value in self.links[date].items():
            link_list.append({"title": key,
                              "href": value})
        return link_list
