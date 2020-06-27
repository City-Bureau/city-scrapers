import json
import re
from datetime import datetime, timedelta

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiBuildingsSpider(CityScrapersSpider):
    name = "chi_buildings"
    agency = "Public Building Commission of Chicago"
    base_url = "https://www.pbcchicago.com/wp-admin/admin-ajax.php?action=eventorganiser-fullcal"  # noqa
    timezone = "America/Chicago"
    start_urls = [
        "{}&start={}&end={}".format(
            base_url,
            (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        )
    ]
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting_types = [
            "admin-opp-committee-meeting",
            "audit-committee",
            "board-meeting",
        ]

        data = json.loads(response.text)
        for item in data:
            if item.get("category") != [] and item.get("category")[0] in meeting_types:
                title, dt_time = self._parse_title_time(item["title"])
                start = self._parse_dt_time(
                    self._parse_datetime(item["start"]), dt_time
                )
                end = self._parse_dt_time(self._parse_datetime(item["end"]), dt_time)
                if end <= start or end.day != start.day:
                    end = None
                meeting = Meeting(
                    title=title,
                    description="",
                    classification=self._parse_classification(item.get("category")[0]),
                    start=start,
                    end=end,
                    time_notes="",
                    all_day=False,
                    source=self._parse_source(item),
                )
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                # Request each relevant event page, including current data in meta attr
                req = scrapy.Request(
                    item["url"], callback=self._parse_event, dont_filter=True,
                )
                req.meta["meeting"] = meeting
                req.meta["category"] = item["category"]
                yield req

    def _parse_title_time(self, title):
        """Return title with time string removed and time if included"""
        time_match = re.search(r"\d{1,2}:\d{2}([ apm.]{3,5})?", title)
        if not time_match:
            return title, None
        time_str = time_match.group()
        title = title.replace(time_str, "").replace("@", "").split(" at ")[0].strip()
        time_str = time_str.strip().replace(".", "")
        # Default to PM if not AM/PM not provided
        if "m" not in time_str:
            time_str = "{} pm".format(time_str)
        return title, datetime.strptime(time_str, "%I:%M %p").time()

    def _parse_event(self, response):
        """
        Parse event detail page if additional information
        """
        meeting = response.meta.get("meeting", {})
        category = response.meta.get("category", ["board-meeting"])
        board_meeting = category[0] in ["board-meeting", "admin-opp-committee-meeting"]
        meeting["location"] = self._parse_location(
            response, board_meeting=board_meeting
        )
        meeting["links"] = self._parse_links(response)
        return meeting

    def _parse_classification(self, meeting_type):
        """
        Parse or generate classification (e.g. town hall).
        """
        if "committee" in meeting_type:
            return COMMITTEE
        elif "board" in meeting_type:
            return BOARD
        return NOT_CLASSIFIED

    def _parse_location(self, item, board_meeting=False):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        if board_meeting:
            return {
                "name": "Second Floor Board Room, Richard J. Daley Center",
                "address": "50 W. Washington Street Chicago, IL 60602",
            }
        if len(item.css(".eo-event-venue-map")) == 0:
            return {
                "name": "",
                "address": "",
            }

        event_script = item.css("script:not([src])")[-1].extract()
        event_search = re.search("var eventorganiser = (.*);", event_script)
        event_details = json.loads(event_search.group(1))
        location = event_details["map"][0]["locations"][0]
        split_tooltip = location["tooltipContent"].split("<br />")
        if "<strong>" in split_tooltip[0]:
            location_name = split_tooltip[0][8:-9]
        else:
            location_name = split_tooltip[0]

        return {
            "name": location_name,
            "address": split_tooltip[1],
        }

    def _parse_dt_time(self, dt, dt_time):
        if dt_time is None:
            dt_time = dt.time()
        return datetime.combine(dt.date(), dt_time)

    def _parse_datetime(self, time_str):
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")

    def _parse_links(self, response):
        """Parse documents if available on previous board meeting pages"""
        links = []
        for doc_link in response.css(
            'a.vc_btn3-shape-rounded, .entry-content a[href*=".pdf"]'
        ):
            links.append(
                {
                    "href": doc_link.attrib["href"],
                    "title": doc_link.xpath("./text()").extract_first().strip(),
                }
            )
        return links

    def _parse_source(self, item):
        """
        Parse source from base URL and event link
        """
        return item["url"]
