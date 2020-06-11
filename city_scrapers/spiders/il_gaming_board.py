import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlGamingBoardSpider(CityScrapersSpider):
    name = "il_gaming_board"
    agency = "Illinois Gaming Board"
    timezone = "America/Chicago"
    start_urls = ["http://www.igb.illinois.gov/MeetingsMinutes.aspx"]
    location = {
        "name": "5th Floor, Michael A Bilandic Building",
        "address": "160 N LaSalle St Chicago, IL 60601",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)

        for item in response.css(".space"):
            item_text = " ".join(item.css(".list *::text").extract()).strip()
            meeting = Meeting(
                title=self._parse_title(item_text),
                description="",
                classification=BOARD,
                start=self._parse_start(item_text),
                end=None,
                all_day=False,
                time_notes="See source to confirm meeting time",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting, text=item_text)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, text):
        """Parse or generate meeting title."""
        if "special" in text.lower():
            return "Riverboat/Video Gaming Special Meeting"
        return "Riverboat/Video Gaming"

    def _parse_start(self, text):
        """Parse start datetime as a naive datetime object."""
        date_str = re.sub(
            r"\s+",
            " ",
            re.search(r"[a-z]{3,10}\s+\d{1,2},?\s+\d{4}", text, flags=re.I).group(),
        ).replace(",", "")
        date_obj = datetime.strptime(date_str, "%B %d %Y").date()
        return datetime.combine(date_obj, time(9))

    def _validate_location(self, response):
        """Confirm that the location has not changed"""
        description = " ".join(response.css(".contentBox > .line *::text").extract())
        if not re.search(r"160\s+N(orth)?\s+LaSalle", description):
            raise ValueError("Meeting location may have changed")

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link_item in item.css(
            "* + .line > .nestedlist > div:not(.clear):not(.hide)"
        ):
            item_type = (
                link_item.css(".meetingLabel::text").extract_first().replace(":", "")
            )
            if "minutes" in item_type.lower():
                item_type = "Minutes"
            for link in link_item.css("a"):
                links.append(
                    {
                        "title": "{}: {}".format(
                            item_type, link.css("*::text").extract_first()
                        ),
                        "href": response.urljoin(link.attrib["href"]),
                    }
                )
        return links
