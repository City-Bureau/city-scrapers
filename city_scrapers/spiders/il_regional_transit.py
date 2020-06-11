import re
from datetime import datetime, time, timedelta

from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlRegionalTransitSpider(CityScrapersSpider):
    name = "il_regional_transit"
    agency = "Regional Transportation Authority"
    timezone = "America/Chicago"
    start_urls = [
        "http://rtachicago.granicus.com/ViewPublisher.php?view_id=5",
        "http://rtachicago.granicus.com/ViewPublisher.php?view_id=4",
    ]
    custom_settings = {"ROBOTSTXT_OBEY": False}
    location = {
        "name": "RTA Administrative Offices",
        "address": "175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604",
    }

    def parse(self, response):
        three_months_ago = datetime.now() - timedelta(days=90)
        for item in response.css(".row:not(#search):not(.keywords)"):
            start = self._parse_start(item)
            if start is None or (
                start < three_months_ago
                and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
            ):
                continue
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
                start=start,
                end=None,
                time_notes="Initial meetings begin at 9:00am, with other daily meetings following",  # noqa
                all_day=False,
                location=self.location,
                links=self._parse_links(item),
                source=(
                    "https://rtachicago.org/about-us/board-meetings/meetings-archive"
                ),
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting)
            yield meeting

    @staticmethod
    def _parse_classification(name):
        name = name.upper()
        if "CITIZENS ADVISORY" in name:
            return ADVISORY_COMMITTEE
        if "COMMITTEE" in name:
            return COMMITTEE
        if "BOARD" in name:
            return BOARD
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_title(item):
        name_text = item.css(".committee::text").extract_first()
        name_text = name_text.split(" on ")[0].split(" (")[0]
        name_text = re.sub(r"\d{1,2}:\d{2}\s+[APM]{2}", "", name_text)
        return name_text.strip()

    @staticmethod
    def _parse_start(item):
        """
        Retrieve the event date, defaulting to 9:00am
        """
        date_str = " ".join(item.css("div:first-child::text").extract()).strip()
        title_str = item.css(".committee::text").extract_first()
        time_obj = time(9, 0)
        time_match = re.search(r"\d{1,2}(:\d{2})? ?[apm\.]{2,4}", title_str)
        if time_match:
            time_str = re.sub(r"[\s\.]", "", time_match.group()).lower()
            time_obj = datetime.strptime(time_str, "%I:%M%p").time()
        date_obj = datetime.strptime(date_str, "%b %d, %Y").date()
        return datetime.combine(date_obj, time_obj)

    @staticmethod
    def _parse_links(item):
        documents = []
        for doc_link in item.css("a"):
            if "onclick" in doc_link.attrib:
                doc_url = re.search(
                    r"(?<=window\.open\(\').+(?=\',)", doc_link.attrib["onclick"]
                ).group()
                if doc_url.startswith("//"):
                    doc_url = "http:" + doc_url
            else:
                doc_url = doc_link.attrib["href"]
            doc_note = doc_link.css("img::attr(alt)").extract_first()
            # Default to link title if alt text for doc icon isn't available
            if doc_note is None:
                if "title" in doc_link.attrib:
                    doc_note = doc_link.attrib["title"]
                else:
                    continue
            if "listen" in doc_note.lower():
                doc_note = "Audio"
            elif "agenda" in doc_note.lower():
                doc_note = "Agenda"
            elif "minutes" in doc_note.lower():
                doc_note = "Minutes"
            elif "video" in doc_note.lower():
                doc_note = "Video"
            documents.append({"href": doc_url, "title": doc_note})
        return documents
