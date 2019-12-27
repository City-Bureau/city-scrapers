import json
import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa69Spider(CityScrapersSpider):
    name = "chi_ssa_69"
    agency = "Chicago Special Service Area #69 95th & Ashland Avenue"
    timezone = "America/Chicago"

    @property
    def start_urls(self):
        today = datetime.now()
        last_week = today - timedelta(days=7)
        in_two_months = today + timedelta(days=60)
        chicago_time_zone = "America/Chicago"

        return [(
            "https://www.googleapis.com/calendar/v3/calendars/gagdcchicago%40gmail.com/events"
            "?calendarId=gagdcchicago@gmail.com&singleEvents=true&timeZone={}&"
            "sanitizeHtml=true&timeMin={}T00:00:00-05:00&timeMax={}T00:00:00-05:00&"
            "key=AIzaSyC-KzxSLmmZitsCVv2DeueeUxoVwP0raVk"
        ).format(
            chicago_time_zone, last_week.strftime("%Y-%m-%d"), in_two_months.strftime("%Y-%m-%d")
        )]

    def parse(self, response):
        data = json.loads(response.text)

        for item in data["items"]:
            title = self._parse_title(item)
            location = self._parse_location(item)
            if not (location and title):
                continue
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(title),
                start=self._parse_dt(item["start"]),
                end=self._parse_dt(item["end"]),
                time_notes="",
                all_day=False,
                location=location,
                links=[],
                source=item["htmlLink"],
            )
            meeting['status'] = self._get_status(meeting, text=item["status"])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, item):
        # ignore CPD and C.A.P.S meetings (tracked elsewhere)
        if "CPD" in item["summary"]:
            return False
        # ignore festivals and things not containing "Meeting" or "SSA"
        elif ("Meeting" not in item["summary"]) and ("SSA" not in item["summary"]):
            return False
        return item["summary"].replace("Meeting", "").strip()

    def _parse_classification(self, title):
        if "committee" in title.lower():
            return COMMITTEE
        elif "commission" in title.lower():
            return COMMISSION
        # we think we can safely return COMMISSION by default
        return COMMISSION

    def _parse_dt(self, dt_obj):
        if "dateTime" in dt_obj:
            return datetime.strptime(dt_obj["dateTime"][:19], "%Y-%m-%dT%H:%M:%S")
        elif "date" in dt_obj:
            return datetime.strptime(dt_obj["date"], "%Y-%m-%d")

    def _parse_location(self, item):
        if "location" not in item:
            return
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

    def _parse_description(self, item):
        return item.get("description", "")
