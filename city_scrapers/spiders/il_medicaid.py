from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlMedicaidSpider(CityScrapersSpider):
    name = "il_medicaid"
    agency = "Illinois Medical Adivsory Committee"
    timezone = "America/Chicago"
    allowed_domains = ["www.illinois.gov"]
    start_urls = ["https://www.illinois.gov/hfs/About/BoardsandCommisions/MAC/Pages/"
                  "MeetingSchedule.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".ctl00_PlaceHolderMain_ctl01_ctl01__ControlWrapper_"
                                 "RichHtmlField ul li"):
            meeting = Meeting(
                title='Medicare Advisory Committee',
                description='',
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location={
                    'name': 'James R. Thompson Center',
                    'address': '100 W Randolph St, 2nd flr. Rm. 2025, Chicago, IL 60601',
                },  # Vid conf with Illinois Department of Healthcare and
                    # Family Service in Springfield.
                links=[],
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    # def _parse_title(self, item):
    #     """Parse or generate meeting title."""
    #     return ""

    # def _parse_description(self, item):
    #     """Parse or generate meeting description."""
    #     return ""

    # def _parse_classification(self, item):
    #     """Parse or generate classification from allowed options."""
    #     return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    # def _parse_time_notes(self, item):
    #     """Parse any additional notes on the timing of the meeting"""
    #     return ""

    # def _parse_all_day(self, item):
    #     """Parse or generate all-day status. Defaults to False."""
    #     return False

    # def _parse_location(self, item):
    #     """Parse or generate location."""
    #     return {
    #         "address": "",
    #         "name": "",
    #     }

    # def _parse_links(self, item):
    #     """Parse or generate links."""
    #     return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
