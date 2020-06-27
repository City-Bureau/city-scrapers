import re
from datetime import datetime, time

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa5Spider(CityScrapersSpider):
    name = "chi_ssa_5"
    agency = "Chicago Special Service Area #5 Commercial Ave"
    timezone = "America/Chicago"
    start_urls = ["http://scpf-inc.org/ssa5/meeting-calendar/"]
    location = {
        "address": "3030 E 92nd St Chicago, IL 60617",
        "name": "MB Financial Bank",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if "3030" not in response.text:
            raise ValueError("Meeting address has changed")

        self.meetings = self._parse_current_year(response)
        yield scrapy.Request(
            "http://scpf-inc.org/ssa5/meeting-minutes/",
            callback=self._parse_minutes,
            dont_filter=True,
        )

    def _parse_current_year(self, response):
        description = " ".join(response.css(".page-post-content *::text").extract())
        self._validate_location(description)

        items = []
        for item in response.css(".page-post-content > *"):
            items.extend(
                [scrapy.Selector(text=s) for s in item.extract().split("<br>")]
            )

        meetings = []
        for item in items:
            item_text = " ".join(item.css("* ::text").extract())
            start = self._parse_start(item_text)
            if not start:
                continue
            meeting = Meeting(
                title=self._parse_title(item_text),
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            meetings.append(meeting)
        return meetings

    def _parse_minutes(self, response):
        """
        Parse the minutes page, matching with existing events if found
        """
        for item in response.css(".page-post-content a"):
            text = item.xpath("text()").extract_first()
            if not text:
                continue
            start = self._parse_start(text, minutes=True)

            links = [{"href": item.attrib["href"], "title": "Minutes"}]
            date_match = [
                idx
                for idx, i in enumerate(self.meetings)
                if i["start"].date() == start.date()
            ]
            if len(date_match):
                self.meetings[date_match[0]]["links"].extend(links)
            else:
                meeting = Meeting(
                    title=self._parse_title(text),
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    time_notes="",
                    all_day=False,
                    location=self.location,
                    links=links,
                    source=response.url,
                )
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                self.meetings.append(meeting)
        for meeting in self.meetings:
            yield meeting

    def _parse_title(self, text):
        """Parse or generate meeting title."""
        if "special" in text.lower():
            return "Special Commission"
        return "Regular Commission"

    def _parse_start(self, text, minutes=False):
        """Parse start datetime."""
        parsed_date = None
        if minutes:
            date_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
            if date_match:
                parsed_date = datetime.strptime(date_match.group(), "%m/%d/%Y")
        else:
            date_match = re.search(r"\w{3,9} \d{1,2}, \d{4}", text)
            if date_match:
                parsed_date = datetime.strptime(date_match.group(), "%B %d, %Y")
        if parsed_date:
            return datetime.combine(parsed_date.date(), time(14))

    def _parse_links(self, item):
        """
        Parse or generate documents.
        """
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()),
                    "href": link.attrib["href"],
                }
            )
        return links

    def _validate_location(self, description):
        """Check that location hasn't changed or raise an exception"""
        if "3030 E" not in description:
            raise ValueError("Meeting location has changed")
