import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class CookForestPreservesSpider(LegistarSpider):
    name = "cook_forest_preserves"
    agency = "Cook County Forest Preserves District"
    timezone = "America/Chicago"
    start_urls = ["https://fpdcc.legistar.com/Calendar.aspx"]

    def parse_legistar(self, events):
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
                classification=self._parse_classification(event["Name"]["label"]),
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )
            meeting["status"] = self._get_status(meeting, event["Meeting Location"])
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_classification(self, name):
        """
        Differentiate board and committee meetings
        based on event name.
        """
        if "board" in name.lower():
            return BOARD
        else:
            return COMMITTEE

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        address = item.get("Meeting Location", None)
        if address:
            address = re.sub(
                r"\s+", " ", re.sub(r"(\n)|(--em--)|(--em)|(em--)", " ", address),
            ).strip()
        return {"address": address, "name": ""}
