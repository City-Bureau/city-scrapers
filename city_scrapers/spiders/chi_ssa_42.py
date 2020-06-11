import re
from datetime import datetime, time

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa42Spider(CityScrapersSpider):
    name = "chi_ssa_42"
    agency = "Chicago Special Service Area #42 71st St/Stony Island"
    timezone = "America/Chicago"
    start_urls = ["https://ssa42.org/ssa-42-meeting-dates/"]
    location = {
        "name": "",
        "address": "1750 E 71st St Chicago, IL 60649",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for meeting in self._parse_meetings(response, upcoming=True):
            yield meeting

        yield scrapy.Request(
            "https://ssa42.org/minutes-of-meetings/", callback=self._parse_meetings,
        )

    def _parse_meetings(self, response, upcoming=False):
        """Parse meetings on upcoming and minutes pages"""
        today = datetime.now().replace(hour=0, minute=0)
        last_year = today.replace(year=today.year - 1)
        for item in response.css("article.entry p"):
            text = item.xpath("./text()").extract_first()
            if not re.match(r".*day, .*\d{4}", text or ""):
                continue
            start = self._parse_start(text)
            if (
                not start
                or (upcoming and start < today)
                or (
                    start < last_year
                    and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                )
            ):
                continue
            meeting = Meeting(
                title=self._parse_title(text),
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
            meeting["status"] = self._get_status(meeting, text=text)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, text):
        """Parse or generate meeting title."""
        name = "SSA #42 Commission"
        if "closed" in text.lower():
            return "{} - Closed Meeting".format(name)
        return name

    def _parse_start(self, text):
        """
        Parse start date and time.
        """
        date_match = re.search(r"[a-zA-Z]{3,9} \d{1,2}([a-z,]{1,3})? \d{4}", text)
        time_match = re.search(r"\d{1,2}:\d{2}[ pam\.]{2,5}", text)
        if date_match:
            try:
                date_str = re.sub(
                    r"(?<=\d)[a-z]{2}", "", date_match.group().replace(",", ""),
                )
                dt = datetime.strptime(date_str, "%B %d %Y").date()
            except ValueError:
                dt = None
        if time_match:
            time_str = time_match.group().replace(".", "").replace(" ", "")
            tm = datetime.strptime(time_str, "%I:%M%p").time()
        else:
            tm = time(10)
        if dt:
            return datetime.combine(dt, tm)

    def _parse_links(self, item):
        """Parse or generate links."""
        docs = []
        for doc in item.css("a"):
            doc_text = doc.xpath("./text()").extract_first()
            if "agenda" in doc_text.lower():
                doc_note = "Agenda"
            elif "minutes" in doc_text.lower():
                doc_note = "Minutes"
            else:
                doc_note = doc_text
            docs.append({"href": doc.attrib["href"], "title": doc_note})
        return docs
