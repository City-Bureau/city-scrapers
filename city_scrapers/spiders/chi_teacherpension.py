import re
from collections import defaultdict
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiTeacherPensionSpider(CityScrapersSpider):
    name = "chi_teacherpension"
    agency = "Chicago Teachers Pension Fund"
    timezone = "America/Chicago"
    start_urls = ["https://www.ctpf.org/board-trustees-meeting-minutes"]
    location = {
        "name": "CTPF Office",
        "address": "203 N LaSalle St, Suite 2600 Chicago, IL 60601",
    }
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def __init__(self, *args, **kwargs):
        self.month_year_minutes = defaultdict(list)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._parse_minutes(response)
        yield scrapy.Request(
            "https://www.boarddocs.com/il/ctpf/board.nsf/XML-ActiveMeetings",
            callback=self._parse_boarddocs,
            dont_filter=True,
        )

    def _parse_minutes(self, response):
        """Parse all past board meeting minutes, store for association to meetings"""
        for minutes_link in response.css(".file > a"):
            link_text = minutes_link.css(".link-text::text").extract_first().strip()
            month_year_match = re.search(r"\w{3,12}\s+\d{4}", link_text)
            if month_year_match:
                month_year = re.sub(r"\s+", " ", month_year_match.group()).strip()
                link_title = "Minutes"
                if "executive" in link_text.lower():
                    link_title = "Executive Session Minutes"
                self.month_year_minutes[month_year].append(
                    {
                        "href": response.urljoin(
                            minutes_link.xpath("@href").extract_first()
                        ),
                        "title": link_title,
                    }
                )

    def _parse_boarddocs(self, response):
        """Parse meetings from BoardDocs XML feed"""
        for item in response.xpath("//meeting"):
            title = self._parse_title(item)
            start = self._parse_start(item)
            classification = self._parse_classification(title)
            source = self._parse_source(item)
            if (
                "historical"
                in (item.xpath("description/text()").extract_first() or "").lower()
            ):
                continue
            meeting = Meeting(
                title=title,
                description="",
                classification=classification,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(start, classification, source, item),
                source=source or response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = item.xpath("name/text()").extract_first()
        if "board of trustees" in title_str.lower():
            return "Board of Trustees"
        # Return first part of string before any "at 3:30 P.M"...
        return re.split(r"\s+at\s+\d", title_str)[0].replace("Meeting", "").strip()

    def _parse_classification(self, title):
        """Parse classification for board or committee meetings."""
        if "board" in title.lower():
            return BOARD
        else:
            return COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime"""
        start_date_str = item.xpath("start/date/text()").extract_first()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        desc = item.xpath("description/text()").extract_first()
        title = item.xpath("name/text()").extract_first()
        time_re = re.compile(r"\d{1,2}:\d{2} [APM\.]{2,4}")
        time_match = time_re.search(title)
        if not time_match and desc is not None:
            time_match = time_re.search(desc)
        if time_match:
            time_match_str = time_match.group().strip().replace(".", "").upper()
            time_obj = datetime.strptime(time_match_str, "%I:%M %p")
            return datetime.combine(start_date.date(), time_obj.time())
        return start_date

    def _parse_location(self, item):
        desc = item.xpath("description/text()").extract_first()
        if desc and "425 S" in desc:
            return {
                "name": "",
                "address": "425 S Financial Place, Suite 1500, Chicago, IL 60605",
            }
        if desc and not re.search(r"203 N[\.orth]*? LaSalle", desc):
            raise ValueError("Meeting location has changed")
        return self.location

    def _parse_links(self, start, classification, source, item):
        """Attach board meeting minutes if for a board meeting"""
        links = [{"title": "Agenda", "href": source}]
        if classification == BOARD:
            links.extend(self.month_year_minutes[start.strftime("%B %Y")])
        return links

    def _parse_source(self, item):
        """Source is also a link to the agenda"""
        return item.xpath("link/text()").extract_first()
