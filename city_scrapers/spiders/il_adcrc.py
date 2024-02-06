import re
from datetime import datetime

from bs4 import BeautifulSoup
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlAdcrcSpider(CityScrapersSpider):
    name = "il_adcrc"
    agency = "Illinois African Descent Citizens Reparations Commission"
    timezone = "America/Chicago"
    start_urls = ["https://adcrc.illinois.gov/meetings.html"]

    def parse(self, response):
        """
        Retrieve the upcoming meetings URL from the main page, which is a JSON feed,
        and then parse the JSON to get the meeting details.
        """
        upcoming_meetings_url = response.css(
            ".cmp-news-feed::attr(data-news-feed-url)"
        ).get()
        if not upcoming_meetings_url:
            self.logger.error("No upcoming meetings found")
            return
        yield response.follow(upcoming_meetings_url, self.parse_json)

    def parse_json(self, response):
        """Parse the JSON feed to get the meeting details."""
        json = response.json()
        for item in json["eventFeedItemList"]:
            meeting = Meeting(
                title=item["eventTitle"],
                description=self._parse_description(item),
                classification=COMMISSION,
                start=self._parse_datetime(item["start"]),
                end=self._parse_datetime(item["end"]),
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )
            meeting["status"] = self._get_status(meeting, item)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_description(self, item):
        """Parse meeting description. In most cases, the description appears
        to be empty. If so, we default to providing info about the virtual
        meeting.
        """
        if item.get("description"):
            return item["description"]
        elif item.get("virtualList"):
            html_content = item["virtualList"][0]["additionalInfo"]
            soup = BeautifulSoup(html_content, "html.parser")
            plain_text = soup.get_text(separator=" ", strip=True)
            normalized_text = re.sub(r"\s+", " ", plain_text).strip()
            return normalized_text
        return ""

    def _parse_datetime(self, datetime_str):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")

    def _parse_location(self, item):
        """Parse or generate location."""
        if not item.get("physicalList") or len(item["physicalList"]) == 0:
            return {
                "address": "",
                "name": "TBD",
            }
        location = item["physicalList"][0]
        name = location["locationName"].replace("In-Person: ", "")
        address = (
            f"{location['streetLineOne']}, {location['city']}, {location['state']}"
        )
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        """Generate links based on virtual link details."""
        if not item.get("virtualList"):
            return ""
        virtualLocation = item["virtualList"][0]
        return [
            {"href": virtualLocation["link"], "title": virtualLocation["locationName"]}
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _get_status(self, meeting, item):
        """Checks the cancelation status first and then passes a "canceled" string
        to the parent's _get_status method so we can rely on default status handling."""
        if item.get("canceledEvent") and item["canceledEvent"] == "true":
            return super()._get_status(meeting, text="canceled")
        return super()._get_status(meeting)
