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

        return [(
            "https://www.googleapis.com/calendar/v3/calendars/gagdcchicago%40gmail.com/events"
            "?calendarId=gagdcchicago@gmail.com&singleEvents=true&timeZone=-05:00&"
            "sanitizeHtml=true&timeMin={}T00:00:00-05:00&timeMax={}T00:00:00-05:00&"
            "key=AIzaSyC-KzxSLmmZitsCVv2DeueeUxoVwP0raVk"
        ).format(
            last_week.strftime("%Y-%m-%d"),
            in_two_months.strftime("%Y-%m-%d"),
        )]

    def create_url(self):
        today = datetime.now()
        last_week = today - timedelta(days=7)
        in_two_months = today + timedelta(days=60)

        # I think the time in the url below is GMT -5:00 which was
        # probably set up for the Detroit scraper I stole this code from
        # I think it will be incorrect for Chicago
        # Should I go with GMT -6:00 ?
        # Actually, now that I am looking up the time online, it looks
        # like GMT -5 is not correct for Detroit, should be GMT -4
        # Is the time off on the Detroit scraper due to Daylght Savings?
        return [(
            "https://www.googleapis.com/calendar/v3/calendars/gagdcchicago%40gmail.com/events"
            "?calendarId=gagdcchicago@gmail.com&singleEvents=true&timeZone=-05:00&"
            "sanitizeHtml=true&timeMin={}T00:00:00-05:00&timeMax={}T00:00:00-05:00&"
            "key=AIzaSyC-KzxSLmmZitsCVv2DeueeUxoVwP0raVk"
        ).format(
            last_week.strftime("%Y-%m-%d"),
            in_two_months.strftime("%Y-%m-%d"),
        )]

    def parse(self, response):
        data = json.loads(response.text)
        print(self.start_urls)
        # exit()
        print(data)
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
                all_day=False,
                location=location,
                links=[],
                source=response.url,
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
        """Parse or generate meeting description."""
        try:
            # not sure if I should format this differently
            return item['description']
        except Exception:
            return ""

    def _parse_classification_old(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        if 'Dates:' in item:
            print('have to deal with multiple dates')
            return 'have to deal with multiple dates'
        elif ' through ' in item:
            # looks like a date range as opposed to a single day
            print('have to deal with date range')
            return 'have to deal with date range'
        elif 'Date:' in item:
            # inner_date_string = re.findall(r"(?:Date).*", item)
            inner_date_string = item.split("Date: ", 1)[-1]

            return inner_date_string

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

    def _parse_location_old(self, item):
        """Parse or generate location."""
        address = ""
        name = ""
        item_str = str(item)
        address_regex = r"((?i)\d+ ((?! \d+ ).)*(il|illinois)(, \d{5}| \d{5}|\b))"
        address_matches = re.findall(address_regex, item_str)
        assert len(address_matches) < 2
        if len(address_matches) > 0:
            address = address_matches[0][0]
            # take care of unicode non-breaking space \xa0
            address = address.replace(u'\xa0', u' ')
        else:
            name = item_str
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]
