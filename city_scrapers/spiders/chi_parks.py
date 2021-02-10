from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class ChiParksSpider(LegistarSpider):
    name = "chi_parks"
    agency = "Chicago Park District"
    timezone = "America/Chicago"
    start_urls = ["https://chicagoparkdistrict.legistar.com/Calendar.aspx"]

    def parse_legistar(self, events):
        three_months_ago = datetime.today() - timedelta(days=90)
        for event in events:
            start = self.legistar_start(event)
            if not start or (
                start < three_months_ago
                and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
            ):
                continue
            meeting = Meeting(
                title=self._parse_title(event),
                description="",
                classification=self._parse_classification(event),
                start=start,
                end=None,
                all_day=False,
                time_notes="Estimated 2 hour duration",
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )
            meeting["status"] = self._get_status(
                meeting, text=meeting["location"]["address"]
            )
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        loc_item = item.get("Meeting Location", "")
        if isinstance(loc_item, dict):
            loc_str = loc_item.get("label", "")
        else:
            loc_str = loc_item
        if "Virtual" in loc_str:
            return {"name": "Virtual", "address": ""}
        return {
            "address": loc_str,
            "name": "",
        }

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        board_str = "Board of Commissioners"
        if item["Name"].strip() == board_str:
            return board_str
        return "{}: {}".format(board_str, item["Name"])

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings.
        """
        if "hearing" in item["Name"].lower():
            return FORUM
        return BOARD

