import re
from datetime import datetime
from io import BytesIO, StringIO

import scrapy
from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFSyntaxError


class IlFinanceAuthoritySpider(CityScrapersSpider):
    name = "il_finance_authority"
    agency = "Illinois Finance Authority"
    timezone = "America/Chicago"
    start_urls = ["https://www.il-fa.com/public-access/board-documents/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse(self, response):
        for item in response.css("tr:nth-child(1n+2)"):
            pdf_link = self._get_pdf_link(item)
            if pdf_link is None or not pdf_link.endswith(".pdf"):
                continue
            date = self._parse_date(item)
            title = self._parse_title(item)
            meeting_info_dict = dict()
            meeting_info_dict["title"] = title
            meeting_info_dict["date"] = date

            yield scrapy.Request(
                response.urljoin(pdf_link),
                callback=self._parse_schedule,
                dont_filter=True,
                meta={"meeting_info_dict": meeting_info_dict},
            )

    def _parse_schedule(self, response):
        """Parse PDF and then yield to meeting items"""
        location, time = self._parse_agenda_pdf(response)
        meeting_info_dict = response.meta["meeting_info_dict"]
        meeting_info_dict["location"] = location
        meeting_info_dict["time"] = time
        yield scrapy.Request(
            response.url,
            callback=self._parse_meeting,
            dont_filter=True,
            meta={"meeting_info_dict": meeting_info_dict},
        )

    def _parse_agenda_pdf(self, response):
        try:
            lp = LAParams(line_margin=0.1)
            out_str = StringIO()
            extract_text_to_fp(
                inf=BytesIO(response.body),
                outfp=out_str,
                maxpages=1,
                laparams=lp,
                codec="utf-8",
            )

            pdf_content = out_str.getvalue().replace("\n", "")
            # Remove duplicate spaces
            clean_text = re.sub(r"\s+", " ", pdf_content)
            # Remove underscores
            clean_text = re.sub(r"_*", "", clean_text)

            location = self._parse_location(clean_text)
            time = self._parse_start(clean_text)
            return location, time
        except PDFSyntaxError as e:
            print("~~Error: " + str(e))

    def _get_pdf_link(self, item):
        pdf_tag = item.css("td:nth-child(4) > a")
        if not (pdf_tag):
            return None
        pdf_link = pdf_tag[0].attrib["href"]
        return pdf_link

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        try:
            title = item.css("td:nth-child(3)::text").extract_first()
            return title
        except TypeError:
            return ""

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "Comm" in title:
            return COMMITTEE
        if "Board" in title:
            return BOARD
        return COMMISSION

    def _parse_location(self, pdf_content):
        try:
            """Parse or generate location."""
            address_match = re.search(
                r"(?:in\s*the|at\s*the) .*(\. | \d{5})", pdf_content
            )
            address = address_match.group(0)
            name = re.findall(r"(?:in\s*the|at\s*the).*?,", pdf_content)[0]
        except Exception:
            address = "Address Not Found"
            name = "Name Not Found"
        return {"address": address, "name": name}

    def _parse_meeting(self, response):
        meeting_info_dict = response.meta["meeting_info_dict"]
        title = meeting_info_dict["title"]
        date = meeting_info_dict["date"]
        time = meeting_info_dict["time"]
        location = meeting_info_dict["location"]

        meeting_start = date + " " + time
        meeting_start = meeting_start.replace(", ", ",").strip()

        meeting = Meeting(
            title=title,
            description=self._parse_description(),
            classification=self._parse_classification(title),
            start=datetime.strptime(meeting_start, "%b %d,%Y %I:%M %p"),
            end=None,
            all_day=False,
            time_notes=self._parse_time_notes(),
            location=location,
            links=self._parse_links(response.url, title),
            source=self._parse_source(response),
        )
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_description(self):
        """Pase or generate meeting description."""
        return ""

    def _parse_date(self, item):
        """Parse start datetime as a naive datetime object."""
        try:
            date_str = item.css("td:nth-child(2)::text").extract_first()
            return date_str
        except TypeError:
            return ""

    def _parse_start(self, pdf_content):
        """Parse start datetime as a naive datetime object."""
        try:
            time = re.findall(r"\d{1,2}:\d{2}\s?(?:A.M.|P.M.|PM|AM)", pdf_content)[0]
            return time
        except Exception:
            return "12:00 AM"

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_links(self, link, title):
        """parse or generate links."""
        return [{"href": link, "title": title}]

    def _parse_source(self, response):
        """parse or generate source."""
        return response.url
