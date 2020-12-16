import json
import re
from datetime import datetime, timedelta
from io import BytesIO, StringIO

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


class IlSexOffenderManagementSpider(CityScrapersSpider):
    name = "il_sex_offender_management"
    agency = "Illinois Sex Offender Management Board"
    timezone = "America/Chicago"
    custom_settings = {"ROBOTSTXT_OBEY": False}
    start_urls = [
        "https://www2.illinois.gov/idoc/Pages/SexOffenderManagementBoard.aspx"
    ]  # noqa
    meeting_minutes = []

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # first go through and gather list of lists for meeting minutes
        for link in response.css(".soi-article-content a"):
            link_text = " ".join(link.css("*::text").extract())
            if ("meeting minutes") in link_text.lower():
                # create new list holding meeting minutes date and link
                date_time_obj = self._get_datetime_obj_meeting_minutes(
                    link_text
                )  # noqa
                href = response.urljoin(link.attrib["href"])
                self.meeting_minutes.append([date_time_obj, href])

        for link in response.css(".soi-article-content a"):
            link_text = " ".join(link.css("*::text").extract())
            if "meeting" not in link_text.lower():
                continue
            if "agenda" in link_text.lower():
                # scrape agenda pdf for meeting information
                yield scrapy.Request(
                    response.urljoin(link.attrib["href"]),
                    callback=self._parse_documents,
                    dont_filter=True,
                )
            # special case where link to video was uploaded rather than agenda
            if "webex" in link_text.lower():
                yield scrapy.Request(
                    link.attrib["href"], callback=self._parse_meta_video
                )

    def _parse_meta_video(self, response):
        """Parse through meta of response in JSON if link provided rather than PDF"""
        meta_text = response.css(
            "[type='application/json']#extendedData::text"
        ).extract_first()
        if not meta_text:
            return
        meta_text = meta_text.strip()
        clean_text_vid = json.loads(meta_text)

        start_time, end_time = self._video_start_end_time(clean_text_vid)

        meeting = Meeting(
            title="MANAGEMENT BOARD",
            description="",
            classification=BOARD,
            start=start_time,
            end=end_time,
            all_day=False,
            time_notes="",
            location={
                "address": "",
                "name": "WebEx Meeting (See meeting links to confirm)",
            },
            links=self._make_links(None, start_time),
            source=response.url,
        )
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _video_start_end_time(self, clean_text_vid):
        """Parse through JSON and return start, end naive datetime objects"""

        # get date time formatted as '2020-09-16 13:00'
        date_time = clean_text_vid["meetingData"]["startTime"][:-3]

        # get meeting duration represented in minutes
        scheduled_duration = clean_text_vid["meetingData"]["scheduledDuration"]

        # create start and end time datetime naive objects
        start_time = datetime.strptime("{}".format(date_time), "%Y-%m-%d %H:%M")

        end_time = start_time + timedelta(minutes=scheduled_duration)

        return start_time, end_time

    def _parse_documents(self, response):
        """Parse meeting information from agenda PDF"""

        links_dict = {
            "title": "Meeting Agenda",
            "href": response.url,
        }
        clean_text = self._cleanUpPDF(response)

        start_time = self._parse_start(clean_text)

        meeting = Meeting(
            title="MANAGEMENT BOARD",
            description="",
            classification=BOARD,
            start=start_time,
            end=self._parse_end(clean_text),
            all_day=False,
            time_notes="See agenda to confirm details",
            location=self._parse_location(clean_text),
            links=self._make_links(links_dict, start_time),
            source=self.start_urls[0],
        )
        meeting["status"] = self._get_status(meeting, text=clean_text)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _make_links(self, agenda_dict, date_time_obj):
        """Make list of agenda and minutes(if applicable)."""
        links = []
        if agenda_dict is not None:
            links.append(agenda_dict)
        for meeting in self.meeting_minutes:
            if date_time_obj.date() == meeting[0].date():
                # account for training meetings
                if "training" in agenda_dict["href"].lower():
                    if "training" in meeting[1].lower():
                        minutes_dict = {"title": "Meeting Minutes", "href": meeting[1]}
                        links.append(minutes_dict)
                elif "training" not in meeting[1].lower():
                    minutes_dict = {"title": "Meeting Minutes", "href": meeting[1]}
                    links.append(minutes_dict)
        return links

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

    def _parse_start(self, clean_text):
        """Parse start datetime as a naive datetime object."""
        date_str = self._get_meeting_date(clean_text)
        time_str = self._get_start_end_time(clean_text)

        # if meeting is cancelled or no time is provided, default is 12:00am
        if time_str is None:
            return self._get_datetime_obj(date_str, "12:00am")
        return self._get_datetime_obj(date_str, time_str[:7])

    def _parse_end(self, clean_text):
        """Parse end datetime as a naive datetime object."""
        date_str = self._get_meeting_date(clean_text)
        time_str = self._get_start_end_time(clean_text)
        # if meeting is cancelled or no time is provided, default is 12:00am
        if time_str is None:
            return self._get_datetime_obj(date_str, "12:00am")
        return self._get_datetime_obj(date_str, time_str[7:])

    def _get_meeting_date(self, clean_text):
        """Parse meeting agenda for 'Month Day, Year' and returns group"""
        pattern = re.compile(
            r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|"
            r"Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|"
            r"Dec(ember)?)\s+\d{1,2},\s+\d{4}"
        )
        return pattern.search(clean_text).group()

    def _get_start_end_time(self, clean_text):
        """Parse start and end time of meeting from agenda and returns group"""
        pattern = re.compile(
            r"[0-2]?[0-9]:[0-9][0-9][a-zA-Z][a-zA-Z]-"
            r"[0-2]?[0-9]:[0-9][0-9][a-zA-Z][a-zA-Z]"
        )
        if pattern.search(clean_text) is not None:
            return pattern.search(clean_text).group()
        else:
            # in a few specific agendas there are times formatted as '9-10am'
            # instead of 9:00am-10:00am or 09:00am-10:00am
            pattern = re.compile(r"[0-2]?[0-9]-[0-9]?[0-9][a-zA-Z][a-zA-Z]")
            if pattern.search(clean_text) is not None:
                # re-make string to 09:00am-10:00am format from '9-10am'
                new_string = pattern.search(clean_text).group()
                suffix = new_string[-2:]
                start = new_string.split("-")[0] + ":00" + suffix
                end = new_string.split("-")[1][:-2] + ":00" + suffix
                new_string = start + "-" + end
                return new_string
            else:
                return None

    def _get_datetime_obj(self, date_str, time_str):
        """Return Naive Datetime object from date and time strings passed in"""
        pattern = re.compile(r"[0-2]?[0-9]:[0-9][0-9][a-zA-Z][a-zA-Z]")
        time_str = pattern.search(time_str).group()
        # standardize time by converting to military time
        time_str = datetime.strptime(time_str, "%I:%M%p").strftime("%H:%M")
        return datetime.strptime("{} {}".format(date_str, time_str), "%B %d, %Y %H:%M")

    def _get_datetime_obj_meeting_minutes(self, link_text):
        """ Make datetime object for meeting minutes"""
        date = self._get_meeting_date(link_text)
        # tested, this will return the datetime object correct regardless
        # if given full month is given and regardless of capitilization
        date_time_obj = datetime.strptime("{}".format(date), "%B %d, %Y")
        return date_time_obj

    def _parse_location(self, clean_text):
        """Parse or generate location."""
        # Extreme variability in location, default to see meeting details
        return {"address": "", "name": "See meeting details"}
