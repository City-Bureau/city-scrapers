import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa1Spider(CityScrapersSpider):
    name = "chi_ssa_1"
    agency = "Chicago Special Service Area #1-2015"
    timezone = "America/Chicago"
    start_urls = [
        "https://loopchicago.com/about-state-street-ssa1-2015/state-street-commission/"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        location = self._parse_location(response)
        meeting_map = {}
        for item in response.css(".layoutArea li"):
            start = self._parse_start(item)
            if not start:
                continue
            meeting = Meeting(
                title="State Street Commission",
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting, text=item.extract())
            meeting["id"] = self._get_id(meeting)
            if meeting["start"] in meeting_map:
                meeting_map[meeting["start"]]["links"].extend(meeting["links"])
            else:
                meeting_map[meeting["start"]] = meeting
        for meeting in meeting_map.values():
            yield meeting

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date_str = item.css("*::text").extract_first()
        date_match = re.search(r"\w{3,9} \d{1,2}, \d{4}", date_str)
        if date_match:
            # Replace typo on site
            date_match_str = date_match.group().replace("2109", "2019")
            parsed_date = datetime.strptime(date_match_str, "%B %d, %Y")
            return datetime.combine(parsed_date.date(), time(14))

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        if "190 N. State St." in response.text:
            return {
                "address": "190 N State St Chicago, IL 60601",
                "name": "ABC 7 Chicago",
            }
        else:
            raise ValueError("Meeting address has changed")

    def _parse_links(self, item, response):
        """
        Parse or generate documents.
        """
        item_link = item.css("a::attr(href)").extract_first()
        if item_link:
            return [
                {
                    "href": response.urljoin(item_link),
                    "title": "Agenda" if "agenda" in item_link.lower() else "Minutes",
                }
            ]
        return []
