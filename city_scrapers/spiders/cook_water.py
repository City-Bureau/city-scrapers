from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD, COMMITTEE, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class CookWaterSpider(LegistarSpider):
    name = "cook_water"
    agency = "Metropolitan Water Reclamation District of Greater Chicago"
    event_timezone = "America/Chicago"
    start_urls = ["https://mwrd.legistar.com"]
    address = "100 East Erie Street Chicago, IL 60611"

    def parse_legistar(self, events):
        three_months_ago = datetime.today() - timedelta(days=90)
        for event, _ in events:
            title = self._parse_title(event)
            start = self.legistar_start(event)
            if (
                title == "Study Session"
                or not start
                or (
                    start < three_months_ago
                    and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                )
            ):
                continue
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
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
        Parse or generate classification (e.g. town hall).
        """
        if "committee" in name.lower():
            return COMMITTEE
        if "hearing" in name.lower():
            return FORUM
        return BOARD

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            "name": item.get("Meeting Location", None),
            "address": self.address,
        }

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item["Name"]["label"]
