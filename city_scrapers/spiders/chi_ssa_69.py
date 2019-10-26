import json
import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION, COMMITTEE, FORUM, NOT_CLASSIFIED
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

        # I think there is a problem where the timezone in Chicago will be
        # changing during tis two month period

        from dateutil import tz

        # determine the current GMT offset for Chicago time (varies throughout the year)
        current_chicago_time = datetime.now(tz.gettz('America/Chicago'))
        current_chicago_time_gmt_offset = str(current_chicago_time)[-6:]
        # print(current_chicago_time)
        # print(current_chicago_time_gmt_offset)

        return [(
            "https://www.googleapis.com/calendar/v3/calendars/gagdcchicago%40gmail.com/events"
            "?calendarId=gagdcchicago@gmail.com&singleEvents=true&timeZone={}&"
            "sanitizeHtml=true&timeMin={}T00:00:00{}&timeMax={}T00:00:00{}&"
            "key=AIzaSyC-KzxSLmmZitsCVv2DeueeUxoVwP0raVk"
        ).format(
            current_chicago_time_gmt_offset,
            last_week.strftime("%Y-%m-%d"), current_chicago_time_gmt_offset,
            in_two_months.strftime("%Y-%m-%d"), current_chicago_time_gmt_offset
        )]

    def parse(self, response):
        data = json.loads(response.text)
        # print(self.start_urls)

        # exit()
        # print(data)
        # exit()
        for item in data["items"]:
            title = self._parse_title(item)
            location = self._parse_location(item)
            if not location:
                continue
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(title),
                start=self._parse_dt(item["start"]),
                end=self._parse_dt(item["end"]),
                time_notes="",
                all_day=self._parse_all_day(item),
                location=location,
                links=[],
                # source=response.url,
                source=item["htmlLink"],
            )
            meeting['status'] = self._get_status(meeting, text=item["status"])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, item):
        return re.sub(r" Meeting$", "", item["summary"].strip())

    def _parse_classification(self, title):
        if "committee" in title.lower():
            return COMMITTEE
        elif "focus group" in title.lower():
            return FORUM
        elif "commission" in title.lower():
            return COMMISSION
        return NOT_CLASSIFIED

    def _parse_dt(self, dt_obj):
        if "dateTime" in dt_obj:
            return datetime.strptime(dt_obj["dateTime"][:19], "%Y-%m-%dT%H:%M:%S")
        elif "date" in dt_obj:
            return datetime.strptime(dt_obj["date"], "%Y-%m-%d")

    def _parse_location(self, item):
        # print(item["location"])
        print(item)
        # if item["location"] != '7901 S Racine Ave, Chicago, IL 60620, USA':
        # exit()
        if "location" not in item:
            return
        split_loc = re.split(r"(?<=[a-z]), (?=\d)", item["location"])
        name = ""
        if len(split_loc) == 1:
            address = split_loc[0]

            # Sometimes they put a room name in the location field and
            # and address in the description
            if (
                "Chicago" not in address and "Il" not in address
                and "006th district police station" in address
            ):
                name = address
                lines_in_desc = re.split(r"\n", item["description"])
                for line in lines_in_desc:
                    if "Chicago" in line:
                        address = line

        else:
            name = split_loc[0]
            address = ", ".join(split_loc[1:])
        return {
            "name": name,
            "address": address,
        }

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        try:
            # not sure if I should format this differently
            return item['description']
        except Exception:
            return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        # Since I don't see a calendar field for allDay
        # I am going to set this to True if the lenght of the meeting
        # is greater than 4 hours
        meeting_duration = self._parse_dt(item["end"]) - self._parse_dt(item["start"])
        print(str(meeting_duration))
        if (meeting_duration > timedelta(hours=4)):
            return True
        else:
            return False

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]
