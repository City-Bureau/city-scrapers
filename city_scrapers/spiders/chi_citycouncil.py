from datetime import datetime, timedelta

from city_scrapers_core.constants import CITY_COUNCIL
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class ChiCityCouncilSpider(LegistarSpider):
    name = "chi_citycouncil"
    agency = "Chicago City Council"
    timezone = "America/Chicago"
    start_urls = ["https://chicago.legistar.com/Calendar.aspx"]
    link_types = ["Notice"]

    def parse_legistar(self, events):
        """
        `parse_legistar` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        three_months_ago = datetime.today() - timedelta(days=90)
        for event, _ in events:
            start = self.legistar_start(event)
            if not start or (
                start < three_months_ago
                and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
            ):
                continue
            meeting = Meeting(
                title=event["Name"]["label"],
                description="",
                classification=CITY_COUNCIL,
                start=start,
                end=None,
                all_day=False,
                time_notes="Estimated 2 hour duration",
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )

            meeting["status"] = self._get_status(
                meeting, text=event["Meeting Location"]
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        split_location = item["Meeting Location"].split(" -- ")
        loc_name = "City Hall"
        if len(split_location) > 0:
            loc_name = "{}, City Hall".format(split_location[0])
        return {
            "address": "121 N LaSalle St Chicago, IL 60602",
            "name": loc_name,
        }
