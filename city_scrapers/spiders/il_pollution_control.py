import json
import re
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlPollutionControlSpider(CityScrapersSpider):
    name = "il_pollution_control"
    agency = "Illinois Pollution Control Board"
    timezone = "America/Chicago"
    domain = "https://pcb.illinois.gov"
    start_urls = [
        domain + "/ClerksOffice/GetCalendarEvents",
    ]
    calendar_page = "https://pcb.illinois.gov/ClerksOffice/Calendar"
    default_links = [
        {
            "title": "Agendas",
            "href": "https://pcb.illinois.gov/CurrentAgendas",
        },
        {
            "title": "Meeting minutes",
            "href": "https://pcb.illinois.gov/ClerksOffice/MeetingMinutes",
        },
    ]

    def parse(self, response):
        data = json.loads(response.text)
        for item in data:
            title = item.get("CalendarTypeDesc")
            if not title or "holiday" in title.lower():
                continue
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_datetime(item.get("StartDateTime")),
                end=self._parse_datetime(item.get("EndDateTime")),
                all_day=item.get("IsFullDay"),
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self.calendar_page,
            )
            meeting["status"] = self._get_status(meeting, text=item.get("Cancelled"))
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_datetime(self, date_str):
        """Parse the datetime from the string format in the JSON"""
        if date_str:
            return datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
        return None

    def _parse_description(self, item):
        """
        Extract and clean text from HTML description using Scrapy selectors,
        removing hidden characters and non-standard whitespace.
        """
        description_html = item.get("Description", "")
        selector = scrapy.Selector(text=description_html)
        text_lines = selector.xpath("//text()").extract()
        clean_text = " ".join(line.strip() for line in text_lines if line.strip())
        # Using regex to remove non-printable characters and other unwanted symbols
        clean_description = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", clean_text)
        return clean_description

    def _parse_classification(self, item):
        if "Board" in item.get("CalendarTypeDesc", ""):
            return BOARD
        return NOT_CLASSIFIED

    def _parse_location(self, item):
        if item.get("Location"):
            return {
                "name": "",
                "address": item["Location"].strip(),
            }
        return {"name": "No location provided", "address": ""}

    def _parse_links(self, item):
        """Parse links from description."""
        description_html = item.get("Description")
        selector = scrapy.Selector(text=description_html)
        a_tags = selector.css("a")
        links = []
        for a_tag in a_tags:
            # check if href is relative or absolute and prefix domain if needed
            href = a_tag.attrib.get("href")
            href_clean = href if href.startswith("http") else self.domain + href
            title = a_tag.attrib.get("title")
            clean_title = title if title else "Related document"
            link = {
                "href": href_clean,
                "title": clean_title,
            }
            links.append(link)
        final_links = self.default_links + links
        return final_links
