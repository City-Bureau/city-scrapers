import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlElectionsSpider(CityScrapersSpider):
    name = "il_elections"
    agency = "Illinois State Board of Elections"
    timezone = "America/Chicago"
    start_urls = ["https://www.elections.il.gov/AboutTheBoard/MeetingMinutesAll.aspx"]
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def __init__(self):
        self.meeting_minutes = dict()
        super().__init__()

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # parse meeting minutes first to associate them with the agenda
        self._parse_minutes(response)

        # parse the agenda
        yield scrapy.Request(
            "https://www.elections.il.gov/AboutTheBoard/Agenda.aspx",
            callback=self._parse_agenda,
            dont_filter=True,
        )

    def _parse_minutes(self, response):
        """Parse all past board meeting minutes, store for association to meetings."""
        minutes = response.css("#ContentPlaceHolder1_gvMeetingMinutes td > a")
        for minute in minutes:
            date = minute.css("::text").extract_first().strip()
            parsed_date = datetime.strptime(date, "%a, %B %d, %Y").date()
            link = minute.css("::attr(href)").extract_first()
            qs = parse_qs(urlparse(link).query)
            self.meeting_minutes[parsed_date] = qs["Doc"][0]

    def _parse_addresses(self, response):
        addresses = dict()
        addr_divs = response.css(".footer-address > div")
        for addr_div in addr_divs:
            # remove "Office" from addr_name, e.g. "Springfield Office"
            addr_name = addr_div.css("p::text").extract_first().split()[0]
            address_lines = addr_div.css("div > div::text").extract()
            # skip last two lines where phone and fax is written
            address = " ".join(
                [line.strip() for line in address_lines[:-2] if line.strip() != ""]
            )
            addresses[addr_name] = address

        return addresses

    def _parse_agenda(self, response):
        """Parse board agenda."""
        addresses = self._parse_addresses(response)

        meetings = response.css("#ContentPlaceHolder1_gvAgenda > tr")[1:-1]
        for item in meetings:
            start = self._parse_start(item)
            location = self._parse_location(item, addresses)
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=start,
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=location,
                links=self._parse_links(item, response, start),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Board of Elections"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return item.css("td")[3].css("::text").extract_first().strip()

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_str = item.css("td")[0].css("::text").extract_first().strip()
        raw_time_str = item.css("td")[1].css("::text").extract_first().strip()
        time_str = re.sub(r"(?<=\d)\.(?=\d)", ":", raw_time_str).replace(".", "")
        return datetime.strptime(f"{date_str} {time_str}", "%a, %B %d, %Y %I:%M %p")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item, addresses):
        """Parse or generate location."""
        name = item.css("td")[2].css("::text").extract_first().strip()
        address = addresses.get(name, "")
        location = {"address": address, "name": ""}
        return location

    def _parse_links(self, item, response, start):
        """Parse or generate links."""
        links = []
        href = item.css("td")[0].css("::attr(href)").extract_first()
        if href:
            qs = parse_qs(urlparse(href).query)
            links.append({"href": response.urljoin(qs["Doc"][0]), "title": "Agenda"})

        if start.date() in self.meeting_minutes:
            links.append(
                {
                    "href": response.urljoin(self.meeting_minutes[start.date()]),
                    "title": "Minutes",
                }
            )

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
