import json
import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMITTEE, POLICE_BEAT
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiPoliceSpider(CityScrapersSpider):
    name = "chi_police"
    agency = "Chicago Police Department"
    timezone = "America/Chicago"
    start_urls = [
        "https://home.chicagopolice.org/wp-content/themes/cpd-bootstrap/proxy/miniProxy.php?https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars/district-1/"  # noqa
    ]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>"  # noqa
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        try:
            data = json.loads(response.body_as_unicode())
        except json.decoder.JSONDecodeError:
            return

        ninety_days_ago = datetime.now() - timedelta(days=90)
        for item in data:
            # Drop events that aren't Beat meetings or DAC meetings
            classification = self._parse_classification(item)
            if not classification:
                continue
            start = self._parse_start(item)
            if start < ninety_days_ago and not self.settings.getbool(
                "CITY_SCRAPERS_ARCHIVE"
            ):
                continue
            end, has_end = self._parse_end(start, item)
            meeting = Meeting(
                title=self._parse_title(classification, item),
                description="",
                classification=classification,
                start=start,
                end=end,
                time_notes="End estimated 2 hours after start" if not has_end else "",
                all_day=False,
                location=self._parse_location(item),
                links=[],
                source=self._parse_source(item),
            )
            meeting["id"] = self._get_id(meeting, identifier=str(item["calendarId"]))
            meeting["status"] = self._get_status(meeting)
            yield meeting

    def _parse_classification(self, item):
        """Classify meeting as District Advisory Council or Beat meeting."""
        if ("district advisory committee" in item["title"].lower()) or (
            "DAC" in item["title"]
        ):
            return COMMITTEE
        elif "beat" in item["title"].lower():
            return POLICE_BEAT

    def _parse_title(self, classification, item):
        """Generate a title based on the classfication."""
        if classification == COMMITTEE:
            return "District Advisory Committee"
        elif classification == POLICE_BEAT:
            return "CAPS District {}, Beat {}".format(
                item["calendarId"], self._parse_beat(item)
            ).strip()
        else:
            return None

    def _parse_beat(self, item):
        """Parse beat identifier from item"""
        district = str(item["calendarId"])
        beat_split = re.sub(r"[\D]+", " ", item["title"]).split()
        beat_list = []
        for beat_num in beat_split:
            if len(beat_num) > 2 and beat_num.startswith(district):
                beat_list.append(beat_num[len(district) :])
            else:
                beat_list.append(beat_num)
        if len(beat_list) == 1:
            return beat_list[0]
        elif len(beat_list) > 1:
            return "{} and {}".format(", ".join(beat_list[:-1]), beat_list[-1])
        return ""

    def _parse_location(self, item):
        """
        Parses location, adding Chicago, IL to the end of the address
        since it isn't included but can be safely assumed.
        """
        if item["location"]:
            address = item["location"] + " Chicago, IL"
            address = re.sub(r"\s+", " ", address).strip()
        else:
            address = None
        return {"address": address, "name": ""}

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(item["start"], "%Y-%m-%dT%H:%M:%S")

    def _parse_end(self, start, item):
        """
        Parse end datetime as a naive datetime object. Returns datetime and whether it
        was parsed
        """
        try:
            return datetime.strptime(item["end"], "%Y-%m-%dT%H:%M:%S"), True
        except TypeError:
            return start + timedelta(hours=2), False

    def _parse_source(self, item):
        return "https://home.chicagopolice.org/office-of-community-policing/community-event-calendars/"  # noqa
