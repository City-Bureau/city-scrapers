import json
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class MinnMacopwdSpider(CityScrapersSpider):
    name = "minn_macopwd"
    agency = "Minneapolis Advisory Committee On People With Disabilities"
    timezone = "America/Chicago"
    base_url = "https://lims.minneapolismn.gov/Calendar/GetCalenderList"
    start_urls = [
        "{}?fromDate={}&toDate={}&meetingType={}&committeeId={}&pageCount={}&offsetStart=0&abbreviation=&keywords=&sortOrder={}".format(
            base_url,
            "Jan 31,2017",
            "",
            2,
            67,
            10000,
            1
        )
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        data = json.loads(response.text)

        for item in data:

            meeting = Meeting(
                title=str(item["CommitteeName"]),
                description=str(item["Description"]),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            if item["Cancelled"]:
                meeting["status"] = self._get_status(meeting, text="Meeting is cancelled")
            else:
                meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(item["MeetingTime"], "%Y-%m-%dT%H:%M:%S")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": item["Address"],
            "name": item["Location"],
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        if item['CommitteeReportDocument']:
            urlDocument = str(item["CommitteeReportDocumentId"]) + "/" + str(item["CommitteeReportDocument"])
            links.append(
                {
                    "title": "Report Document",
                    "href": "https://lims.minneapolismn.gov/Download/CommitteeReport/" + urlDocument,
                }
            )
        return links

    def _parse_source(self, item):
        """
        Parse source from base URL and event link
        """
        return "https://lims.minneapolismn.gov/Download/CommitteeReport/"
