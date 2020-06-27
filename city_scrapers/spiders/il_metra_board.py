import re
from datetime import datetime

from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlMetraBoardSpider(CityScrapersSpider):
    name = "il_metra_board"
    agency = "Illinois Metra"
    timezone = "America/Chicago"
    start_urls = ["https://metrarr.granicus.com/ViewPublisher.php?view_id=5"]
    custom_settings = {"ROBOTSTXT_OBEY": False}
    location = {
        "name": "",
        "address": "547 West Jackson Boulevard, Chicago, IL",
    }

    def parse(self, response):
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for item in response.css(".listingTable .listingRow"):
            start = self._parse_start(item)
            if start < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE"):
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting)
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css("td[headers=Name]::text").extract_first().strip()

    def _parse_classification(self, item):
        """Parse or generate classification (e.g. public health, education, etc)."""
        full_name = item.css("td[headers=Name]::text").extract_first()

        if "Metra" in full_name and "Board Meeting" in full_name:
            return BOARD
        elif "Citizens Advisory" in full_name:
            return ADVISORY_COMMITTEE
        elif "Committee Meeting" in full_name:
            return COMMITTEE
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        raw_date_time = item.css("td[headers~=Date]::text").extract_first()
        date_time_str = re.sub(r"\s+", " ", raw_date_time).strip()

        if not date_time_str:
            return

        try:
            return datetime.strptime(date_time_str, "%b %d, %Y - %I:%M %p")
        except ValueError:
            pass

    def _parse_links(self, item):
        """Parse documents from current and past meetings"""
        documents = []
        agenda_url = item.css("a[href*=Agenda]::attr(href)").extract_first()
        if agenda_url:
            documents.append({"href": agenda_url, "title": "Agenda"})
        minutes_url = item.css("a[href*=Minutes]::attr(href)").extract_first()
        if minutes_url:
            documents.append({"href": minutes_url, "title": "Minutes"})
        video_url = item.css("td[headers~=VideoLink] a::attr(onclick)").extract_first()
        video_url_match = re.search(r"http.*(?=\',\'p)", video_url or "")
        if video_url and video_url_match:
            documents.append({"href": video_url_match.group(), "title": "Video"})
        return documents
