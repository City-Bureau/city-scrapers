import requests
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser


class ChiCitycouncilSpider(CityScrapersSpider):
    name = "chi_citycouncil"
    agency = "Chicago City Council"
    timezone = "America/Chicago"
    start_urls = ["https://chicityclerkelms.chicago.gov/Meetings/"]

    def parse(self, response):
        # The API endpoint
        url = "https://api.chicityclerkelms.chicago.gov/meeting"  # noqa

        # A GET request to the API
        response = requests.get(url)
        response_json = response.json()

        for item in response_json["data"]:
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item["body"]
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        full_date = item["date"]

        date = full_date.split("T")[0]
        time = full_date.split("T")[1]
        time2 = time.split("+")[0]
        return parser().parse(date + " " + time2)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "Please double check the meeting time on the meeting page."

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "City Hall, 121 N LaSalle St - Chicago, IL 60602",
            "name": "City Council Chamber, 2nd Floor",
        }

    def _parse_links(self, item):
        """Parse or generate links."""

        meetind_id = item["meetingId"]
        meeting_page = (
            "https://chicityclerkelms.chicago.gov/Meeting/?meetingId=" + meetind_id
        )

        return [{"href": meeting_page, "title": "Meeting Page"}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
