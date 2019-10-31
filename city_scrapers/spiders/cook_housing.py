import json
import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookHousingSpider(CityScrapersSpider):
    name = "cook_housing"
    agency = "Cook County Housing Authority"
    timezone = "America/Chicago"
    start_urls = ["http://thehacc.org/about/"]
    location = {
        "name": "HACC Central Office Board Room",
        "address": "175 West Jackson, Suite 350, Chicago, IL 60604",
    }

    def parse(self, response):
        self.link_date_map = defaultdict(list)
        for link in response.css(".additional-resources li a"):
            link_title = re.sub(r"\s+", " ", " ".join(link.css("*::text").extract()).strip())
            date_match = re.search(r"[a-zA-Z]{3,10} \d{1,2}([a-z]{2})?,? \d{4}", link_title)
            if not date_match:
                continue
            date_str = re.sub(r"((?<=\d)[a-z]+|,)", "", date_match.group())
            link_date = datetime.strptime(date_str, "%B %d %Y").date()
            if "agenda" in link_title.lower():
                link_title = "Agenda"
            elif "minutes" in link_title.lower():
                link_title = "Minutes"
            self.link_date_map[link_date].append({
                "title": link_title,
                "href": response.urljoin(link.attrib["href"]),
            })

        now = datetime.now()
        for months_delta in range(-2, 3):
            month_str = (now + relativedelta(months=months_delta)).strftime("%Y-%m")
            yield response.follow("/events/{}/".format(month_str), callback=self._parse_calendar)

    def _parse_calendar(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        year_str = re.search(r"\d{4}", response.url).group()
        for event in response.css(".type-tribe_events"):
            item = json.loads(event.attrib["data-tribejson"])
            classification = self._parse_classification(item["title"])
            if classification == BOARD:
                start = self._parse_dt(item["startTime"], year_str)
                meeting = Meeting(
                    title=self._parse_title(item["title"]),
                    description="",
                    classification=BOARD,
                    start=start,
                    end=self._parse_dt(item["endTime"], year_str),
                    all_day=False,
                    time_notes="",
                    location=self._parse_location(item),
                    links=self.link_date_map[start.date()],
                    source=item["permalink"],
                )

                meeting["status"] = self._get_status(meeting, text=item["excerpt"])
                meeting["id"] = self._get_id(meeting)

                yield meeting

    @staticmethod
    def _parse_title(title):
        """Parse or generate meeting title."""
        if "board meeting" in title.lower():
            return "Board of Commissioners"
        return title

    @staticmethod
    def _parse_classification(title):
        """Parse or generate classification from allowed options."""
        if "board" in title.lower():
            return BOARD
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_dt(date_str, year_str):
        """Parse start and end datetimes as a naive datetime object."""
        return datetime.strptime(" ".join([year_str, date_str]), "%Y %B %d @ %I:%M %p")

    def _parse_location(self, item):
        """Parse or generate location."""
        desc_str = item["excerpt"]
        if "175 W" in desc_str:
            return self.location
        addr_match = re.search(r"(?<=[\< ])\d+ .*(?=\<)", item["excerpt"])
        if not addr_match:
            return {
                "name": "TBD",
                "address": "",
            }
        addr_str = addr_match.group()
        if "Chicago" not in addr_str:
            addr_str += " Chicago, IL"
        return {
            "name": "",
            "address": addr_str,
        }
