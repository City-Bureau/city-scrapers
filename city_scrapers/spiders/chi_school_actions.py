import itertools
import re
from datetime import datetime

from city_scrapers_core.constants import FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSchoolActionsSpider(CityScrapersSpider):
    name = "chi_school_actions"
    agency = "Chicago Public Schools"
    timezone = "America/Chicago"
    start_urls = ["http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for school in response.css("#wrapper > table > tr"):
            school_name = school.css("td:first-child span::text").extract_first()
            school_action = (
                school.css("td:nth-child(2) p > span::text").extract_first().strip()
            )
            school_links = self._parse_links(school)

            for meeting_section in school.css(
                "#main-body > table > tr > td > table > tr"
            ):
                meeting_type = self._parse_meeting_type(meeting_section, school_action)
                for item in meeting_section.css("td > table"):
                    start = self._parse_start(item)
                    end = self._parse_end(item)
                    title = self._parse_title(school_name, meeting_type)
                    meeting = Meeting(
                        title=title,
                        description="",
                        classification=FORUM,
                        start=start,
                        end=end,
                        time_notes="",
                        all_day=False,
                        location=self._parse_location(item),
                        links=school_links,
                        source=response.url,
                    )
                    meeting["id"] = self._get_id(meeting)
                    meeting["status"] = self._get_status(meeting)
                    yield meeting

    def _parse_title(self, school_name, meeting_type):
        """Parse or generate event title."""
        return "School Actions: {} {}".format(school_name, meeting_type)

    @staticmethod
    def _parse_meeting_type(item, school_action):
        return "{}: {}".format(
            item.css("td > p.sub-title:first-of-type::text").extract_first(),
            school_action,
        )

    @staticmethod
    def _parse_date_str(item):
        """
        Parse date, return as %Y-%b-%d string
        """
        year = item.css(".year::text").extract_first()
        month = item.css(".month::text").extract_first()
        day = item.css(".day::text").extract_first()
        return "{}-{}-{}".format(year, month, day)

    @staticmethod
    def _parse_datetime_str(date_str, time_str):
        """
        Parse datetime string from date and time strings
        """
        time_match = re.search(
            r"(\d{1,2}(:\d{2})?[apm]{2})", re.sub(r"[\s\.]", "", time_str.lower())
        )
        if not time_match:
            return
        clean_time_str = time_match.group()
        time_format_str = "%I:%M%p"
        if ":" not in time_str:
            time_format_str = "%I%p"
        return datetime.strptime(
            " ".join([date_str, clean_time_str]), "%Y-%b-%d " + time_format_str
        )

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date_str = self._parse_date_str(item)
        time_str = item.css(".time::text").extract_first()
        return self._parse_datetime_str(date_str, time_str.split("-")[0])

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        date_str = self._parse_date_str(item)
        time_str = item.css(".time::text").extract_first()
        split_time = time_str.split("-")
        if len(split_time) > 1:
            return self._parse_datetime_str(date_str, split_time[1])

    @staticmethod
    def _parse_location(item):
        """
        Parses location, adding Chicago, IL to the end of the address
        since it isn't included but can be safely assumed.
        """
        address = item.css(".addr2::text").extract_first()
        return {
            "name": item.css(".addr::text").extract_first(),
            "address": address + " Chicago, IL",
        }

    @staticmethod
    def _parse_links(school):
        """
        Parsing the documentation and meeting note URLs
        """
        doc_link_list = []
        doc_link_items = school.css("ul.bullets:first-of-type li")
        note_link_items = school.css("ul.bullets:nth-of-type(2) li")

        for item in itertools.chain(doc_link_items, note_link_items):
            doc_link_list.append(
                {
                    "title": item.css("a::text").extract_first(),
                    "href": "http://schoolinfo.cps.edu/SchoolActions/"
                    + item.css("a::attr(href)").extract_first(),
                }
            )
        return doc_link_list
