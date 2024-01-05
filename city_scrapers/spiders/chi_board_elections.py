import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiBoardElectionsSpider(CityScrapersSpider):
    name = "chi_board_elections"
    agency = "Chicago Board of Elections"
    timezone = "America/Chicago"
    start_urls = [
        "https://chicagoelections.gov/about-board/board-meetings",
    ]
    location = {
        "name": "Board's Conference Room",
        "address": "Suite 800, 69 West Washington Street, Chicago, Illinois",
    }

    def parse(self, response):
        event = response.css(
            ".block-views.block-views-blockboard-meeting-next-meeting > div > div"
        )

        meeting = Meeting(
            title=self._parse_title(event),
            description="",
            classification=COMMISSION,
            start=self._parse_start(event),
            end=None,
            time_notes="",
            all_day=False,
            location=self.location,
            links=self._parse_links(event),
            source=response.url,
        )
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_title(self, event):
        return event.css("article > h3 > span::text").extract_first()

    def _parse_start(self, event):
        date_string = event.css(".board-meeting--teaser p::text").extract_first()
        date = re.search(r"\w+\s\d+,\s\d{4}", date_string).group()
        start_time = datetime.strptime(date, "%B %d, %Y").replace(
            hour=10, minute=0, second=0
        )
        return start_time

    def _parse_links(self, event):
        links = []
        for atag in event.css("a"):
            links.append(
                {
                    "title": atag.css("::text").extract_first(),
                    "href": atag.css("::attr(href)").extract_first(),
                }
            )
        return links
