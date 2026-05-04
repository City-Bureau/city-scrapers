from datetime import datetime

import scrapy
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparser


class IlRegionalTransitSpider(CityScrapersSpider):
    name = "il_regional_transit"
    agency = "Regional Transportation Authority"
    timezone = "America/Chicago"
    all_meetings_url = "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials?year={year}"  # noqa
    upcoming_meetings_url = "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials"  # noqa

    _location = {
        "name": "RTA Headquarters",
        "address": "175 W. Jackson Blvd., Chicago, IL 60604",
    }

    _time_note = (
        "Check the source page to confirm details on meeting time and location."
    )

    _start_time = "9:00 AM"

    custom_settings = {"ROBOTSTXT_OBEY": False}

    """
    During building the scraper for this source, it was observed
    that some meetings are listed in both the upcoming and archived
    sections of the website. To avoid duplicates, a set is used to
    track meetings that have already been scraped. The meeting title
    and start time are combined to create a unique identifier for each
    meeting, which is then stored in the set. Before yielding a
    meeting, the scraper checks if it has already been seen and skips
    it if it has.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scraped_meetings = set()

    def start_requests(self):
        yield scrapy.Request(
            url=self.upcoming_meetings_url,
            callback=self._get_all_meetings,
        )

    def _get_all_meetings(self, response):
        upcoming_section = response.css(
            ".bg-rtadarkgray-500.w-full.grid.grid-cols-1.p-8.mb-12.border-t-4.border-rtayellow-500"  # noqa
        )

        yield from self.get_upcoming_meetings(upcoming_section)

        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            yield scrapy.Request(
                url=self.all_meetings_url.format(year=year),
                callback=self.parse,
            )

    def get_upcoming_meetings(self, upcoming_section):
        upcoming_meetings = self._parse_upcoming_meetings(upcoming_section)

        for item in upcoming_meetings:
            seen_meeting = str(item["start_time"]) + " " + item["title"]
            if seen_meeting in self._scraped_meetings:
                continue
            self._scraped_meetings.add(seen_meeting)

            meeting = Meeting(
                title=item["title"],
                description="",
                classification=self._parse_classification(item),
                start=item["start_time"],
                end=None,
                all_day=False,
                time_notes=self._time_note,
                location=item["location"],
                links=item["links"],
                source=self.upcoming_meetings_url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def parse(self, response):
        meetings = response.css(
            ".grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3.gap-8.my-6"
        )
        archived_data = meetings.css(
            ".bg-rtadarkgray-500.border-t-4.border-rtayellow-500.p-6"
        )

        archived_meetings = self._parse_archived_meetings(archived_data)

        for item in archived_meetings:
            seen_meeting = str(item["start_time"]) + " " + item["title"]
            if seen_meeting in self._scraped_meetings:
                continue
            self._scraped_meetings.add(seen_meeting)

            meeting = Meeting(
                title=item["title"],
                description="",
                classification=self._parse_classification(item),
                start=item["start_time"],
                end=None,
                all_day=False,
                time_notes=self._time_note,
                location=item["location"],
                links=item["links"],
                source=self.upcoming_meetings_url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_upcoming_meetings(self, upcoming_data):
        meetings = []

        for event in upcoming_data:
            title = event.css(
                ".font-heading.text-xl.md\\:text-2xl.text-white.mb-2::text"
            ).get()
            start_time = event.css(".text-xl.text-rtayellow-500.mb-4::text").get()
            location_strings = event.css("p.text-white.text-sm.mb-4::text").getall()
            links = []

            item = {
                "title": title,
                "start_time": self._parse_start(start_time),
                "location": self._parse_location(location_strings),
                "links": links,
            }
            meetings.append(item)
        return meetings

    def _parse_archived_meetings(self, archived_data):
        meetings = []
        for event in archived_data:
            title = event.css(".text-base.text-rtayellow-500.mb-4::text").get()
            start_time = event.css(".text-lg.text-white.mb-4::text").get()

            item = {
                "title": title,
                "start_time": dateparser(
                    f"{start_time} {self._start_time}"
                    if title == "Board Meeting"
                    else start_time
                ),
                "location": self._location,
                "links": self._parse_links(event),
            }
            meetings.append(item)
        return meetings

    def _parse_location(self, strings):
        return {
            "name": strings[0].strip() if len(strings) > 0 else "",
            "address": strings[1].strip() if len(strings) > 1 else "",
        }

    def _parse_classification(self, item):
        title = item["title"].lower()
        if "citizen advisory" in title:
            return ADVISORY_COMMITTEE
        if "committee" in title:
            return COMMITTEE
        if "board" in title:
            return BOARD
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        start = item.replace("Upcoming:", "").replace(": ", " ").strip()
        return dateparser(start)

    def _parse_links(self, item):
        links = []
        links_container = item.css(".grid.grid-cols-2 a::attr(href)").getall()
        links_title = item.css(".grid.grid-cols-2 h2::text").getall()

        for link, title in zip(links_container, links_title):
            links.append(
                {
                    "title": title,
                    "href": link,
                }
            )
        return links
