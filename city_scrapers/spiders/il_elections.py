from datetime import datetime

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
        self.addresses = dict()
        super().__init__()

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._parse_minutes(response)
        self._parse_addresses(response)
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
            parsed_date = datetime.strptime(date, "%a, %B %d, %Y")
            link = minute.css("::attr(href)").extract_first()
            self.meeting_minutes[parsed_date] = link

    def _parse_agenda(self, response):
        """Parse board agenda."""
        meetings = response.css("#ContentPlaceHolder1_gvAgenda > tr")[1:-1]
        for item in meetings:
            start = self._parse_start(item)
            location = self._parse_location(item)
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
        return "Illinois State Board of Elections"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        desc = item.css("td")[3].css("::text").extract_first().strip()
        return desc

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.css("td")[0].css("::text").extract_first().strip()
        time = item.css("td")[1].css("::text").extract_first().strip().replace(".", "")
        dt = date + " " + time
        parsed_dt = datetime.strptime(dt, "%a, %B %d, %Y %I:%M %p")
        return parsed_dt

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        name = item.css("td")[2].css("::text").extract_first().strip()
        if name in self.addresses:
            address = self.addresses[name]

        return {
            "address": address,
            "name": name,
        }

    def _parse_addresses(self, response):
        addr_divs = response.css(".footer-address > div")
        for addr_div in addr_divs:
            addr_name = addr_div.css("p::text").extract_first()
            address_lines = addr_div.css("div > div::text").extract()
            address = " ".join([line.strip() for line in address_lines if line.strip() != ""])
            self.addresses[addr_name.split()[0]] = address

    def _parse_links(self, item, response, start):
        """Parse or generate links."""
        links = []
        href = item.css("td")[0].css("::attr(href)").extract_first()
        if href:
            href = response.urljoin(href)
        else:
            href = ""

        if start.date() in [i.date() for i in self.meeting_minutes]:
            links.append({
                "href":
                    response.urljoin(
                        self.meeting_minutes[datetime.combine(start.date(), datetime.min.time())]
                    ),
                "title": ""
            })
        links.append({"href": href, "title": ""})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
