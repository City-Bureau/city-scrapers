import json
import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION, COMMITTEE, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class DetCharterReviewSpider(CityScrapersSpider):
    name = "det_charter_review"
    agency = "Detroit Charter Review Commission"
    allowed_domains = ["google.com"]

    @property
    def start_urls(self):
        today = datetime.now()
        last_week = today - timedelta(days=7)
        in_two_months = today + timedelta(days=60)
        return [(
            "https://clients6.google.com/calendar/v3/calendars/detroitcrc2018@gmail.com/events"
            "?calendarId=detroitcrc2018@gmail.com&singleEvents=true&timeZone=GMT-5:0&"
            "sanitizeHtml=true&timeMin={}T00:00:00-05:00&timeMax={}T00:00:00-05:00&"
            "key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"
        ).format(
            last_week.strftime("%Y-%m-%d"),
            in_two_months.strftime("%Y-%m-%d"),
        )]

    def parse(self, response):
        data = json.loads(response.text)
        for item in data["items"]:
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
                start=self._parse_dt(item["start"]["dateTime"]),
                end=self._parse_dt(item["end"]["dateTime"]),
                time_notes="",
                all_day=False,
                location=self._parse_location(item),
                links=[],
                source="https://sites.google.com/view/detroitcharter2018",
            )
            meeting['status'] = self._get_status(meeting, text=item["status"])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, item):
        return item["summary"].strip().rstrip(" Meeting")

    def _parse_classification(self, title):
        if "committee" in title.lower():
            return COMMITTEE
        elif "focus group" in title.lower():
            return FORUM
        return COMMISSION

    def _parse_dt(self, dt_str):
        return datetime.strptime(dt_str[:19], "%Y-%m-%dT%H:%M:%S")

    def _parse_location(self, item):
        split_loc = re.split(r"(?<=[a-z]), (?=\d)", item["location"])
        name = ""
        if len(split_loc) == 1:
            address = split_loc[0]
        else:
            name = split_loc[0]
            address = ", ".join(split_loc[1:])
        return {
            "name": name,
            "address": address,
        }
