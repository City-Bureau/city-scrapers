import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookHospitalsSpider(CityScrapersSpider):
    name = "cook_hospitals"
    agency = "Cook County Health and Hospitals System"
    timezone = "America/Chicago"
    start_urls = [
        "https://cookcountyhealth.org/about/board-of-directors/board-committee-meetings-agendas-minutes/"  # noqa
    ]
    location = {
        "name": "",
        "address": "1950 W Polk St, Conference Room 5301, Chicago, IL 60612",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Only pull from first two year sections because it goes back pretty far
        six_months_ago = datetime.today() - timedelta(days=180)
        for group in response.css(".panel"):
            title = self._parse_title(group)
            for item in group.css("tbody > tr"):
                start = self._parse_start(item)
                if start < six_months_ago and not self.settings.getbool(
                    "CITY_SCRAPERS_ARCHIVE"
                ):
                    continue
                meeting = Meeting(
                    title=title,
                    description="",
                    classification=self._parse_classification(title),
                    start=start,
                    end=None,
                    time_notes="Confirm time in agenda",
                    all_day=False,
                    location=self._parse_location(item),
                    links=self._parse_links(item, response),
                    source=response.url,
                )
                meeting["status"] = self._get_status(
                    meeting, text=" ".join(item.css("td:first-child::text").extract())
                )
                meeting["id"] = self._get_id(meeting)
                yield meeting

    @staticmethod
    def _parse_title(item):
        title_str = " ".join(item.css(".panel-title *::text").extract()).strip()
        if "board" in title_str.lower():
            return "Board of Directors"
        return re.sub(r"\s+Meetings?", "", title_str)

    @staticmethod
    def _parse_start(item):
        """Get start datetime from item's text"""
        date_str = (
            item.css("td:first-child::text").extract_first().strip().replace(" - ", " ")
        )
        try:
            return datetime.strptime(date_str, "%B %d, %Y %I:%M %p")
        except ValueError:
            return datetime.strptime(date_str, "%B %d, %Y")

    @staticmethod
    def _parse_classification(title):
        if "board" in title.lower():
            return BOARD
        return COMMITTEE

    @staticmethod
    def _parse_links(item, response):
        links = []
        for link in item.css('td[data-title="Documents"] > a'):
            links.append(
                {
                    "href": response.urljoin(link.attrib["href"]),
                    "title": " ".join(link.css("::text").extract()).strip(),
                }
            )
        return links

    def _parse_location(self, item):
        """Parse location"""
        loc_text = item.css("td:first-child::text").extract()
        if len(loc_text) < 2 or not loc_text[1].strip() or "5301" in loc_text[1]:
            return self.location
        else:
            return {"name": "", "address": loc_text[1].strip()}
