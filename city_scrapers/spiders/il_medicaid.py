from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime

class IlMedicaidSpider(CityScrapersSpider):
    name = "il_medicaid"
    agency = "Illinois Medical Adivsory Committee"
    timezone = "America/Chicago"
    allowed_domains = ["www.illinois.gov"]
    start_urls = ["file:///Users/ksong/myCodes/open-source/city-scrapers/tests/files/il_medicaid.html"]
    # start_urls = ["https://www.illinois.gov/hfs/About/BoardsandCommisions/MAC/Pages/"
    #               "MeetingSchedule.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        date_x_path = '//div[@id="ctl00_PlaceHolderMain_ctl01_ctl01__ControlWrapper_RichHtmlField"]/ul/li/p/text()'
        for raw_date in response.xpath(date_x_path).getall():
            # Clean up the raw dates
            raw_date = raw_date.replace('\xa0',' ').strip()
            if raw_date.count(',') == 2:
                index = raw_date.find(",")
                raw_date = raw_date[index+1:].strip()
            date = datetime.strptime(raw_date, "%B %d, %Y")

            meeting = Meeting(
                title='Medicare Advisory Committee',
                description='',
                classification=ADVISORY_COMMITTEE,
                start=date.replace(hour=10),
                end=date.replace(hour=12),
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

    # def _parse_start(self, item):
    #     """Parse start datetime as a naive datetime object."""
    #     return None

    # def _parse_end(self, item):
    #     """Parse end datetime as a naive datetime object. Added by pipeline if None"""
    #     return None

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
