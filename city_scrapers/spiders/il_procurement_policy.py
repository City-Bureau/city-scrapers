import re
from collections import defaultdict
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlProcurementPolicySpider(CityScrapersSpider):
    name = "il_procurement_policy"
    agency = "Illinois Procurement Policy Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx",
        "https://www2.illinois.gov/sites/ppb/Pages/board_minutes.aspx",
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if "future" in response.url:
            yield from self._upcoming_meetings(response)
        else:
            yield from self._prev_meetings(response)

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        time_object = time(10, 0)
        date_str = " ".join(item.css("*::text").extract()).strip()
        date_str = re.sub("Agenda.pdf", "", date_str).strip()
        try:
            date_object = datetime.strptime(date_str, "%B %d, %Y").date()
            return datetime.combine(date_object, time_object)
        except ValueError:
            return

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        title_str = " ".join(item.css("*::text").extract()).strip()
        if "pdf" in title_str:
            title_str = re.sub("Agenda.pdf", "", title_str).strip()
            title_str += " Agenda"
        links.append(
            {"title": title_str, "href": response.urljoin(item.attrib["href"])}
        )
        return links

    def _link_date_map(self, response):
        link_map = defaultdict(list)
        for item in response.css(".ms-rtestate-field p a"):
            date = self._past_start(item)
            title_str = date.strftime("%B %d, %Y")
            link_map[date].append(
                {"title": title_str, "href": response.urljoin(item.attrib["href"])}
            )
        for item in response.css(".ms-rtestate-field .list-unstyled li a"):
            date = self._past_start(item)
            if date is None:
                continue
            title_str = date.strftime("%B %d, %Y")
            link_map[date].append(
                {"title": title_str, "href": response.urljoin(item.attrib["href"])}
            )
        return link_map

    def _past_start(self, item):
        """parse or generate links from past meetings"""
        str_list = [".docx", ".pdf", "-", "["]
        time_object = time(10, 0)
        date_str = " ".join(item.css("*::text").extract()).strip()
        if len(date_str) == 0:
            return None
        date_str = date_str.replace("\u200b", "")
        index = None
        for item in str_list:
            if item in date_str:
                index = date_str.index(item)
                break
        date_str = date_str[:index]
        date_object = datetime.strptime(date_str.strip(), "%B %d, %Y").date()
        return datetime.combine(date_object, time_object)

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _upcoming_meetings(self, response):
        for item in response.css(".ms-rtestate-field p strong a"):
            start = self._parse_start(item)
            if not start:
                continue
            meeting = Meeting(
                title="Procurement Policy Board",
                description="",
                classification=self._parse_classification(item),
                start=start,
                all_day=False,
                time_notes="",
                location={
                    "name": "Stratton Office Building",
                    "address": "401 S Spring St, Springfield, IL 62704",
                },
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _prev_meetings(self, response):
        meets = self._link_date_map(response)
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for item in meets:
            if item < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE"):
                continue
            meeting = Meeting(
                title="Procurement Policy Board",
                description="",
                classification=BOARD,
                start=item,
                all_day=False,
                time_notes="",
                location={
                    "name": "Stratton Office Building",
                    "address": "401 S Spring St, Springfield, IL 62704",
                },
                links=meets[item],
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting
