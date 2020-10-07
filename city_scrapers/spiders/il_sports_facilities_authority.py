from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class IlSportsFacilitiesAuthoritySpider(CityScrapersSpider):
    name = "il_sports_facilities_authority"
    agency = "Illinois Sports Facilities Authority"
    timezone = "America/Chicago"
    start_urls = ["https://www.isfauthority.com/governance/board-meetings/"]
    location = {
        "name": "Authority offices",
        "address": "Guaranteed Rate Field, 333 West 35th Street, Chicago, IL",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)

        item = response.css(".wpb_wrapper .inner-text h2::text").getall()[0]
        meeting_title, _, next_meeting_time = item.partition(":")
        meeting = Meeting(
            title=meeting_title,
            description="",
            classification=BOARD,
            start=self._parse_next_start(next_meeting_time),
            end=None,
            all_day=False,
            time_notes="",
            location=self.location,
            links=[],
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

        for item in response.css(".wpb_wrapper p")[2:]:
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _validate_location(self, response):
        location_text = response.css(".wpb_wrapper p strong::text").getall()[1]
        if "Guaranteed Rate Field" not in location_text:
            raise ValueError("Meeting location has changed")

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        parts = item.css("::text").get().split()
        return " ".join(parts[:-1])

    def _parse_next_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return parse(item)

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        parts = item.css("::text").get().split()
        return parse(parts[-1])

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "href": link.attrib["href"],
                    "title": " ".join(link.css("::text").getall()),
                }
            )
        return links

    def _parse_classification(self, item):
        meeting_title = item.css("::text").get()
        if "Board" in meeting_title:
            return BOARD
        return COMMITTEE
