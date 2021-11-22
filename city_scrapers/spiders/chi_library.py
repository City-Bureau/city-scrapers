import datetime
import re

import requests
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLibrarySpider(CityScrapersSpider):
    name = "chi_library"
    agency = "Chicago Public Library"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chipublib.org/board-of-directors/board-meeting-schedule/"
    ]

    def __init__(self, *args, session=requests.Session(), **kwargs):
        """
        Initialize a spider with a session object to use for determining whether
        documents exist
        """
        super().__init__(*args, **kwargs)
        self.session = session

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        year = re.search(
            r"\d+", response.css("#content h1::text").extract_first()
        ).group()
        for item in response.css("div.entry-content p"):
            if len(item.css("strong")) == 0:
                continue
            start = self._parse_start(item, year)
            meeting = Meeting(
                title="Board of Directors",
                description="",
                classification=BOARD,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(start),
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting)
            yield meeting

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        addr_str = item.css("::text")[-1].extract().strip()
        if "virtual" in addr_str.lower():
            return {
                "name": "Virtual",
                "address": "",
            }
        addr_str = "{} Chicago, IL".format(addr_str)
        return {
            "name": item.css("a::text").extract_first() or "",
            "address": addr_str,
        }

    def _parse_start(self, item, year):
        """
        Parse start date and time.
        """
        dt_str = item.css("strong::text").extract()[-1]
        return datetime.datetime.strptime(
            "{} {}".format(re.sub(r"[,\.]", "", dt_str), year), "%A %B %d %I %p %Y"
        )

    def _parse_links(self, start_time):
        """Check if agenda and minutes are valid URLs, add to documents if so"""
        agenda_url = (
            "https://www.chipublib.org/news/board-of-directors-"
            "meeting-agenda-{}-{date.day}-{date.year}/"
        ).format(start_time.strftime("%B").lower(), date=start_time,)
        minutes_url = agenda_url.replace("agenda", "minutes")
        agenda_res = self.session.get(agenda_url)
        minutes_res = self.session.get(minutes_url)
        documents = []
        if agenda_res.status_code == 200:
            documents.append({"href": agenda_url, "title": "Agenda"})
        if minutes_res.status_code == 200:
            documents.append({"href": minutes_url, "title": "Minutes"})
        return documents
