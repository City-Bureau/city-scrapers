import re
from collections import defaultdict
from datetime import datetime, time
from enum import Enum

from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlInvestmentPolicySpider(CityScrapersSpider):
    name = "il_investment_policy"
    agency = "Illinois Investment Policy Board"
    timezone = "America/Chicago"
    start_urls = ["https://www2.illinois.gov/sites/iipb/Pages/MeetingInformation.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        links_map = self._parse_links(response)

        for meeting in self._parse_upcoming_meetings(response, links_map):
            yield meeting

        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for item in response.xpath(
            "//h2[text()='Agendas']/following-sibling::ul"
            "[not(preceding-sibling::h2[text()='Minutes'])]"
            "/li/p"
        ):
            start = self._parse_start(item)
            if start < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE"):
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=start,
                end=None,
                all_day=False,
                time_notes="Confirm start time with agency.",
                location={
                    "name": "James R. Thompson Center",
                    "address": "100 W. Randolph St., Room 16-503, Chicago, Illinois",
                },
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            meeting_type = self._parse_meeting_type(meeting["title"])
            meeting["links"] = links_map.get(
                (meeting["start"].date(), meeting_type), []
            )

            yield meeting

    def _parse_upcoming_meetings(self, response, links_map):
        meetings = []
        upcoming = response.xpath(
            "//strong[text()='2019 Board Meetings']/following::ul[1]"
        )
        for item in upcoming.xpath("./li"):
            ddate_str = item.xpath("text()").get().strip()
            ddate = datetime.strptime(ddate_str, "%m/%d/%y").date()
            if (ddate, IlInvestmentPolicyMeetingType.IIPB) not in links_map.keys():
                meeting = Meeting(
                    title="Investment Policy Board",
                    description="",
                    classification=BOARD,
                    start=datetime.combine(ddate, time(11, 00)),
                    end=None,
                    all_day=False,
                    time_notes="Confirm start time with agency.",
                    location={
                        "name": "James R. Thompson Center",
                        "address": "100 W. Randolph St., Room 16-503, Chicago, Illinois",  # noqa
                    },
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                meeting["links"] = []

                meetings.append(meeting)
        return meetings

    @staticmethod
    def _parse_title(
        item,
        ise_substrings=["ise", "sudan", "iran"],
        ibr_substrings=["ibr", "israel"],
        iipb_substrings=["iipb", "policy", "board"],
    ):
        """Parse or generate meeting title."""
        title = item.xpath("text()[normalize-space(.)]").get().lstrip(" -").strip()
        if any(substring in title.lower() for substring in ise_substrings):
            return "Committee on Sudan and Iran Restrictions"
        elif any(substring in title.lower() for substring in ibr_substrings):
            return "Committee on Israel Boycott Restrictions"
        elif any(substring in title.lower() for substring in iipb_substrings):
            return "Investment Policy Board"
        return title

    @staticmethod
    def _parse_classification(
        item, board_substrings=["board", "iipb"], committee_substrings=["committee"]
    ):
        """Parse or generate classification from allowed options."""
        title = item.xpath("text()[normalize-space(.)]").get()
        if any(substring in title.lower() for substring in board_substrings):
            return BOARD
        elif any(substring in title.lower() for substring in committee_substrings):
            return COMMITTEE
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_meeting_type(
        text,
        ise_substrings=["ise", "sudan", "iran"],
        ibr_substrings=["ibr", "israel"],
        iipb_substrings=["iipb", "policy", "board"],
    ):
        if any(substring in text.lower() for substring in ise_substrings):
            return IlInvestmentPolicyMeetingType.ISE
        elif any(substring in text.lower() for substring in ibr_substrings):
            return IlInvestmentPolicyMeetingType.IBR
        elif any(substring in text.lower() for substring in iipb_substrings):
            return IlInvestmentPolicyMeetingType.IIPB
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        link_text = item.xpath("a/text()[normalize-space(.)]").get()
        return datetime.combine(self._parse_date(link_text), time(11, 00))

    def _parse_links(self, response):
        """
        Extracts links for a specific meeting date
        """
        link_map = defaultdict(list)
        for item in response.xpath("//h2[text()='Agendas']/following-sibling::ul/li/p"):
            title = item.xpath("text()[normalize-space(.)]").get()
            link = item.xpath("a")
            link_text_selector = link.xpath("text()")
            if len(link_text_selector) > 1:
                link_text_selector = link_text_selector[1]
            if (
                link_text_selector
                and link_text_selector.get().lstrip(" -").strip() != ""
            ):
                link_text = link_text_selector.get().lstrip(" -").strip()
                if title is None:
                    title = link_text
                link_date = self._parse_date(link_text)
                meeting_type = self._parse_meeting_type(title)
                link_map[(link_date, meeting_type)].append(
                    {
                        "href": response.urljoin(link.xpath("@href").get()),
                        "title": link_text,
                    }
                )
        return link_map

    @staticmethod
    def _validate_location(response):
        """Throws a ValueError if the location has changed from the original location"""
        location = "James R. Thompson Center"
        text = response.xpath(
            "//h2[text()='Agendas']/preceding-sibling::p[1]/text()"
        ).get()
        if location not in text:
            raise ValueError("Meeting address has changed")

    @staticmethod
    def _parse_date(source):
        """Returns date"""
        match = re.search(r"(\d+[.]\d+[.]\d+)", source)
        if match:
            return datetime.strptime(match.group(1), "%m.%d.%y").date()
        match = re.search(r"(\d+[ ]\d+[ ]\d+)", source)
        if match:
            return datetime.strptime(match.group(1), "%m %d %y").date()
        match = re.search(r"(\S+ \d+, \d{4})", source)
        if match:
            return datetime.strptime(match.group(1), "%B %d, %Y").date()
        match = re.search(r"(\S+ \d+ \d{4})", source)
        if match:
            return datetime.strptime(match.group(1), "%B %d %Y").date()
        match = re.search(r"(\d+-\d+-\d{4})", source)
        if match:
            return datetime.strptime(match.group(1), "%m-%d-%Y").date()
        match = re.search(r"(\d+-\d+-\d{2})", source)
        if match:
            return datetime.strptime(match.group(1), "%m-%d-%y").date()


class IlInvestmentPolicyMeetingType(Enum):
    ISE = 1
    IBR = 2
    IIPB = 3
