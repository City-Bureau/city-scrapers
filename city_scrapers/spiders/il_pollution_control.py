from collections import defaultdict
from datetime import datetime
import json

from scrapy import Request

from city_scrapers_core.constants import BOARD, FORUM, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlPollutionControlSpider(CityScrapersSpider):
    name = "il_pollution_control"
    agency = "Illinois Pollution Control Board"
    timezone = "America/Chicago"
    allowed_domains = ["pcb.illinois.gov"]
    start_urls = ["https://pcb.illinois.gov/ClerksOffice/MeetingMinutes"]

    def __init__(self, *args, **kwargs):
        self.link_map = defaultdict(list)  # Populated by self._parse_minutes()
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        # Gather links to meeting minutes, to be associated with Meeting objects later:
        self._parse_minutes(response)

        # Parse JSON containing meeting data:
        yield Request("https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents", callback=self._parse_json)

    def _parse_minutes(self, response):
        """ Populate self.link_map """
        return None

    def _parse_json(self, response):
        """ Parse JSON from https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents -> Meetings """
        data = json.loads(response.body_as_unicode())

        for item in data:
            if item["CalendarTypeDesc"] == "Holiday":
                continue  # Not a meeting - just an indication of a holiday on the calendar.
            title = item["CalendarTypeDesc"].replace("CANCELLED", "").strip()
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(title),
                start=self._parse_start(item),
                end=None,
                all_day=item["IsFullDay"],
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            # meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            print(meeting)
            yield meeting

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "Board" in title:
            return BOARD
        elif "Seminar" in title:
            return FORUM
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        return datetime.strptime(item["StartDateTime"], '%m/%d/%Y %H:%M:%S %p')

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
