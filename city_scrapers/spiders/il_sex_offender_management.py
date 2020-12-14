from city_scrapers_core.constants import BOARD, CANCELLED, PASSED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from datetime import datetime
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
                # scrape agenda pdf for meeting information
                yield scrapy.Request(
                    response.urljoin(link.attrib["href"]),
                    callback=self._parse_documents,
                    dont_filter=True,
                )

    def _parse_documents(self, response):
        """Parse meeting information from agenda PDF"""

        links_dict =  {
                        "title": "Meeting Agenda",
                        "href": response.urljoin(""),
                     }
        cleanText = self._cleanUpPDF(response)

        #import pdb; pdb.set_trace();

        if self._parse_status(cleanText) == CANCELLED:
            meeting = Meeting(
                title="SEX OFFENDER MANAGEMENT BOARD",
                description="",
                classification=BOARD,
                start=self._parse_start(cleanText),
                end=self._parse_end(cleanText),
                all_day=False,
                time_notes="See agenda to confirm details",
                location={
                    "address": "",
                    "name": "Meeting Cancelled",
                },
                links=links_dict,
                source=self.start_urls[0]
            )
            meeting["status"] = self._get_status(meeting, text="Meeting is cancelled")
            meeting["id"] = self._get_id(meeting)

        else:
            meeting = Meeting(
                title="SEX OFFENDER MANAGEMENT BOARD",
                description="",
                classification=BOARD,
                start= self._parse_start(cleanText),
                end=self._parse_end(cleanText),
                all_day=False,
                time_notes="See agenda to confirm details",
                location=self._parse_location(cleanText),
                links=links_dict,
                source=self.start_urls[0]
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

        yield meeting

    def _cleanUpPDF(self, response):
        """Clean up and return text string of PDF"""
        lp = LAParams(line_margin=0.1)
        out_str = StringIO()
        extract_text_to_fp(BytesIO(response.body), out_str, laparams=lp)
        pdf_text = out_str.getvalue().replace("\n", "")
        # Remove duplicate characters not followed by lowercase (as in 5:00pm)
        clean_text = re.sub(r"([A-Z0-9:])\1(?![a-z])", r"\1", pdf_text, flags=re.M)
        # Remove duplicate spaces
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text

    def _parse_status(self, cleanText):
        """Check if meeting was/is cancelled."""
        if "meeting is cancelled" in cleanText.lower():
            return CANCELLED
        # I went through every agenda PDF, for meetings that weren't either
        # cancelled or moved, the agenda began with "Welcome/Roll Call"
        if "Welcome/Roll Call" not in cleanText:
            return CANCELLED
        return PASSED


    def _parse_start(self, cleanText):
        """Parse start datetime as a naive datetime object."""
        date_str = self._get_meeting_date(cleanText)
        time_str = self._get_start_end_time(cleanText)

        # if meeting is cancelled or no time is provided, default is 12:00
        if time_str is None:
            return self._get_datetime_obj(date_str, "12:00")
        return self._get_datetime_obj(date_str, time_str[:7])

    def _parse_end(self, cleanText):
        """Parse end datetime as a naive datetime object."""
        date_str = self._get_meeting_date(cleanText)
        time_str = self._get_start_end_time(cleanText)
        # if meeting is cancelled or no time is provided, default is 12:00
        if time_str is None:
            return self._get_datetime_obj(date_str, "12:00")
        return self._get_datetime_obj(date_str, time_str[7:])

    def _get_meeting_date(self, cleanText):
        """Parse meeting agenda for 'Month Day, Year' and returns group"""
        pattern = re.compile(
            "(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|"
            "Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|"
            "Dec(ember)?)\s+\d{1,2},\s+\d{4}")
        return pattern.search(cleanText).group()

    def _get_start_end_time(self, cleanText):
        """Parse start and end time of meeting from agenda and returns group"""
        pattern = re.compile(
                                "[0-2]?[0-9]:[0-9][0-9][a-zA-Z][a-zA-Z]-"
                                "[0-2]?[0-9]:[0-9][0-9][a-zA-Z][a-zA-Z]"
                            )
        return pattern.search(cleanText).group()

    def _get_datetime_obj(self, date_str, time_str):
        pattern = re.compile("[0-2]?[0-9]:[0-9][0-9][a-zA-Z][a-zA-Z]")
        time_str = pattern.search(time_str).group()
        # standardize time by converting to military time
        time_str = datetime.strptime(time_str, '%I:%M%p').strftime('%H:%M')
        return datetime.strptime(
            "{} {}".format(date_str, time_str), "%B %d, %Y %H:%M"
        )


    def _parse_location(self, cleanText):
        """Parse or generate location."""
        # there were different locations depending on if the meeting was
        # a video conference, a phone conference, or a physical location.
        # I hardcoded in the most frequent addresses as there were quite a few
        # different locations, but I have made sure to note that one should conirm
        # the address is indeed correct before using.

        name = ""
        address = ""

        if "video conference" in cleanText.lower():
            name = """Video Conference (see meeting links to confirm address since
            it often changes and there can be more than one meeting method)"""
            address = """IDOC, 1301 Concordia Court, Executive Building Conference Room, Springfield
                        and/or IDOC 100 West Randolph, Suite 4-20 Chicago, IL 60601"""

        elif "location" in cleanText.lower():
            name = """Physical Location (see meeting links to confirm address since
            it often changes and there can be more than one meeting method)"""
            address = "Illinois State Police, 800 Old Airport Road, Pontiac"

        elif "phone conference" in cleanText.lower():
            name = """Phone Conference (see meeting links to confirm address since
            it often changes and there can be more than one meeting method)"""
            address = "Call in number: 888-494-4032  Pass Code: 7094957981"

        return {
            "address": name,
            "name": address,
        }
