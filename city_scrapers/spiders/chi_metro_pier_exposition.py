from datetime import datetime, time

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiMetroPierExpositionSpider(CityScrapersSpider):
    name = "chi_metro_pier_exposition"
    agency = "Chicago Metropolitan Pier and Exposition Authority"
    timezone = "America/Chicago"
    start_urls = ["http://www.mpea.com/mpea-board-members/"]
    location = {
        "name": "MPEA Corporate Center",
        "address": "301 E Cermak Rd, Corporate Boardroom, 5th Floor, Chicago, IL 60616",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        description = " ".join(
            response.css(".vc_col-sm-6 .wpb_wrapper p *::text").extract()
        )
        # Cancelled meetings don't show the address,
        # but otherwise should be in the description
        if "cancel" not in description.lower() and "301 East Cermak" not in description:
            raise ValueError("Meeting location has changed")
        for item in response.css(".supsystic-table tr")[3:]:
            title = self._parse_title(item)
            classification = self._parse_classification(title)
            meeting = Meeting(
                title=title,
                description="",
                classification=classification,
                start=self._parse_start(item, classification),
                end=None,
                all_day=False,
                time_notes="Refer to notice for start time",
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(
                meeting, text=item.css("td:nth-child(2)::text").extract_first() or ""
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = item.css("td:nth-child(2)::text").extract_first()
        if "committee" in title_str.lower():
            return title_str.replace("Meeting", "").strip()
        return "Board of Directors"

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        return BOARD

    def _parse_start(self, item, classification):
        """Parse start datetime as a naive datetime object."""
        date_str = item.css("td::text").extract_first().strip()
        date_obj = datetime.strptime(date_str, "%B %d, %Y").date()
        time_obj = time(9)
        if classification == COMMITTEE:
            time_obj = time(13, 30)
        return datetime.combine(date_obj, time_obj)

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "href": link.attrib["href"],
                    "title": link.xpath("./text()").extract_first(),
                }
            )
        return links
