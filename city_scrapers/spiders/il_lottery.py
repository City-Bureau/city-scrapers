import re
from collections import defaultdict
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlLotterySpider(CityScrapersSpider):
    name = "il_lottery"
    agency = "Illinois Lottery Control Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.illinoislottery.com/illinois-lottery/lottery-control-board/"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        if "122 South Michigan Avenue, 19th Floor" not in response.text:
            raise ValueError("Meeting address has changed")

        upcoming_meetings = self._parse_upcoming_meetings(response)
        past_meetings = self._parse_past_meetings(response)
        links = self._parse_links(response)

        # create a master dictionary with one key per meeting date
        reconciled_meetings = upcoming_meetings
        only_past_dates = set(past_meetings.keys()).difference(upcoming_meetings.keys())
        only_past_meetings = {
            key: value for key, value in past_meetings.items() if key in only_past_dates
        }
        reconciled_meetings.update(only_past_meetings)

        for key in sorted(reconciled_meetings.keys(), reverse=True):
            item = reconciled_meetings[key]
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location={
                    "name": "Chicago Lottery Office",
                    "address": "122 South Michigan Avenue, 19th Floor, Chicago, IL 60603",  # noqa
                },
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting, text=item)
            meeting["links"] = links.get(meeting["start"].date(), [])

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        suffix = ""
        if "QTR" in item:
            suffix = "Quarterly "
        elif "Special" in item:
            suffix = "Special "
        return "Lottery Control Board {}Meeting".format(suffix)

    @staticmethod
    def parse_time(source):
        """Returns times given string with format h:mm am|pm"""
        time_regex = re.compile(r"([1-9]:[0-5][0-9]\s?[a|p]m)")

        try:
            time_match = time_regex.search(source).group().replace(" ", "")
            return datetime.strptime(time_match, "%I:%M%p").time()
        except AttributeError:
            default_hour = 13
            default_minute = 30
            return time(default_hour, default_minute)

    @staticmethod
    def parse_day(source):
        """Returns date"""
        # search for dates with '/' (ex: 08/16/19)
        if "/" in source:
            date_match = re.search(r"(\d{2}\/\d{2}\/\d{2})", source).group()
            dt = datetime.strptime(date_match, "%m/%d/%y").date()
        # search for date in format "[month] [dd], [yyyy]" (ex: 'May 15, 2019')
        else:
            date_match = re.search(r"[a-zA-Z]{3,10} \d{1,2}?,? \d{4}", source).group()
            dt = datetime.strptime(date_match, "%B %d, %Y").date()

        return dt

    def _parse_start(self, item):
        """Parse start date and time."""
        return datetime.combine(self.parse_day(item), self.parse_time(item))

    def _parse_links(self, response, link_text_substrings=["Agenda", "Minutes"]):
        """
        Extracts link to agenda for a specific meeting date
        Args:
            date: A datetime object with the date of the desired agenda
            link_text_substrings: A list with strings that must exist in link text
                in order to be added to link dictionary
        Return:
            List of dictionaries with the keys title (title/description of the link)
            and href (link URL) for the agenda for the meeting on the requested date
        """
        link_date_map = defaultdict(list)
        for link in response.xpath("//p//a"):
            link_text_selector = link.xpath("text()")
            if link_text_selector:
                link_text = link_text_selector.get()
                if any(
                    link_text_substring in link_text
                    for link_text_substring in link_text_substrings
                ):
                    link_date = self.parse_day(link_text)
                    link_href = link.xpath("@href").get()
                    link_date_map[link_date].append(
                        {
                            "href": response.urljoin(link_href),
                            "title": link_text.replace("\xa0", " "),
                        }
                    )

        return link_date_map

    def _parse_upcoming_meetings(self, response):
        """
        Returns a list of lines with dates following the string 'Upcoming Meeting Dates'
        """

        meeting_xpath = '//p[contains(., "Upcoming meeting dates")]'

        # future meetings are separated by <br> tags
        meeting_lines = response.xpath(meeting_xpath).css("p *::text").extract()

        special_meeting_xpath = '//p[contains(., "Special meeting of")]'
        special_meeting_lines = (
            response.xpath(special_meeting_xpath).css("p *::text").extract()
        )
        # only keep lines that include a weekday
        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        meeting_lines = [
            x for x in meeting_lines if any(weekday in x for weekday in weekdays)
        ]
        special_meeting_lines = [
            "Special " + line
            for line in special_meeting_lines
            if any(weekday in line for weekday in weekdays)
        ]

        meetings = {}
        for meeting_text in meeting_lines + special_meeting_lines:
            meeting_date = self.parse_day(meeting_text)
            meetings = self._update_meeting_value(meetings, meeting_date, meeting_text)

        return meetings

    def _parse_past_meetings(self, response):
        """Returns a list of start date and documents from meeting minutes page"""
        meetings = {}
        for item in response.css("a"):
            meeting_text = item.xpath("text()").get()
            if meeting_text is not None:
                if "Agenda" in meeting_text or "Minutes" in meeting_text:
                    meeting_date = self.parse_day(meeting_text)
                    meetings = self._update_meeting_value(
                        meetings, meeting_date, meeting_text
                    )
        return meetings

    def _update_meeting_value(self, meetings, meeting_date, meeting_text):
        """
        Updates the meetings dictionary
        If date does not yet exist in dictionary, adds to dictionary
        If date already exists, updates value with additional text found for the meeting

        Args:
            meetings: Dict where key = date and value = text associated with the meeting
            meeting_date: A datetime object representing a meeting date
            meeting_text: A string with information about a meeting
        Return:
            An updated version of the meetings dictionary
        """
        if meetings.get(meeting_date) is None:
            meetings[meeting_date] = meeting_text
        else:
            meetings[meeting_date] = meetings[meeting_date] + " " + meeting_text
        return meetings
