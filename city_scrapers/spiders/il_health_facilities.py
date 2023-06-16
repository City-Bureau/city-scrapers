from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, FORUM, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlHealthFacilitiesSpider(CityScrapersSpider):
    name = "il_health_facilities"
    agency = "Illinois Health Facilities and Services Review Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://www2.illinois.gov/sites/hfsrb/events/Pages/Board-Meetings.aspx"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your
        scraping needs.
        """
        links = response.css("a")
        parsed_links = []
        for link_element in links:
            inner_link_element = link_element.css("h3")

            if inner_link_element:
                href = link_element.attrib["href"]

                parsed_links.append(href)

        for link in parsed_links:
            yield scrapy.http.Request(link, callback=self.parse_event_page)

    def parse_event_page(self, response):
        # An example demonstrating the structure of the time data on the page:
        # <div class="soi-event-data">
        #     <h2>When</h2>
        #     Tuesday, March 21, 2023
        #     <br/>
        #     9:00 AM - 4:00 PM
        # </div>
        time_data = response.css("div.soi-event-data").get()

        time_data = time_data.replace("\r", "").replace("\t", "").replace("\n", "")

        time_data = time_data.split("</h2>")[1].split("<br>")

        date_list = time_data[0].strip().split(" ")

        year = date_list[3].strip(",").strip()

        month = date_list[1].strip(",").strip()

        day = date_list[2].strip(",").strip()

        time_list = time_data[1].split()

        start_hr = time_list[0].split(":")[0]

        start_min = time_list[0].split(":")[1]

        end_hr = time_list[3].split(":")[0]

        end_min = time_list[3].split(":")[1]

        start_meridiem = time_list[1]

        end_meridiem = time_list[4]

        start_date_time = datetime.strptime(
            f"{year}_{month}_{day}_{start_hr}_{start_min}_{start_meridiem}",
            "%Y_%B_%d_%I_%M_%p",
        )

        end_date_time = datetime.strptime(
            f"{year}_{month}_{day}_{end_hr}_{end_min}_{end_meridiem}",
            "%Y_%B_%d_%I_%M_%p",
        )

        meeting = Meeting(
            title=self._parse_title(response),
            description=self._parse_description(response),
            classification=self._parse_classification(response),
            start=start_date_time,
            end=end_date_time,
            all_day=self._parse_all_day(response),
            time_notes=self._parse_time_notes(response),
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=self._parse_source(response),
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        # The structure of the html section where we parse the title
        # is as follows:
        # <div class="row container soi-pagetitle-wrapper">
        #     <div class="col-sm-12 soi-pagetitle">
        #         <h1>
        #             March 21, 2023 State Board Meeting
        #         </h1>
        #     </div>
        # </div>

        title = item.css("h1::text").get().strip()
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""

        # Structure for the html we need to parse:
        # <p class="soi-eventType">
        #   <strong>Event Type: </strong>
        #       Board Meeting
        # </p>

        event_type_string = item.css("p.soi-eventType").get()
        event_type_string = event_type_string.split("</strong>")[1].strip().lower()

        if "board" in event_type_string:
            return BOARD

        elif "forum" in event_type_string:
            return FORUM
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

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

        # The address data for this webpage is a little malformed

        location_str1 = item.css("div.soi-event-title::text").get().strip()
        location_str2 = item.css("div.soi-event-location-address1::text").get().strip()
        location_str3 = item.css("div.soi-event-location-address2::text").get().strip()

        address_string = location_str1 + ", " + location_str2 + location_str3

        address_string = address_string.replace("`", "")

        return {
            "address": address_string,
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""

        links = [
            {
                "href": "https://www2.illinois.gov/sites/hfsrb/events/Pages/Board-Meetings.aspx",  # noqa
                "title": "Board and Subcommittee Meetings",
            },
            {
                "href": "https://www2.illinois.gov/sites/hfsrb/events/Pages/Previous-Meetings.aspx",  # noqa
                "title": "Previous Meeting",
            },
            {
                "href": "https://www2.illinois.gov/sites/hfsrb/events/Pages/Public-Hearing.aspx",  # noqa
                "title": "Public Hearings",
            },
        ]

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
