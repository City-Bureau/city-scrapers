from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError, parse


class IlSportsFacilitiesAuthoritySpider(CityScrapersSpider):
    name = "il_sports_facilities_authority"
    agency = "Illinois Sports Facilities Authority"
    timezone = "America/Chicago"
    start_urls = ["https://www.isfauthority.com/governance/board-meetings/"]
    location = {
        "name": "Authority offices, Guaranteed Rate Field",
        "address": "333 W 35th St, Chicago, IL 60616",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)

        item = response.css("#post-area h2::text").getall()[0]
        meeting = Meeting(
            title=self._parse_title(item.partition(":")[0]),
            description="",
            classification=self._parse_classification(item),
            start=self._parse_next_start(item),
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

        for item in response.css("#post-area p"):
            start = self._parse_start(item)
            if not start:
                continue
            meeting = Meeting(
                title=self._parse_title(
                    " ".join(item.css("::text").get().split()[:-1])
                ),
                description="",
                classification=self._parse_classification(item.css("::text").get()),
                start=start,
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
        location_text = " ".join(response.css("#post-area strong::text").getall())
        if "Guaranteed Rate Field" not in location_text:
            raise ValueError("Meeting location has changed")

    def _parse_title(self, meeting_title):
        """Parse or generate meeting title."""
        if "Committee" not in meeting_title and "Special" not in meeting_title:
            return "Board of Directors"
        if "Meeting" in meeting_title and "Special" not in meeting_title:
            meeting_title = meeting_title.replace("Meeting", "").strip()
        return meeting_title

    def _parse_next_start(self, item):
        """Parse start datetime as a naive datetime object."""
        _, _, next_meeting_time = item.partition(":")
        return parse(next_meeting_time)

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        parts = item.css("::text").get().split()
        if len(parts) == 0:
            return
        try:
            return parse(parts[-1])
        except ParserError:
            return

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
        if "Board" in item:
            return BOARD
        return COMMITTEE
