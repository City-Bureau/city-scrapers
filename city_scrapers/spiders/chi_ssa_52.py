from datetime import datetime
from difflib import SequenceMatcher

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa52Spider(CityScrapersSpider):
    name = "chi_ssa_52"
    agency = "Chicago Special Service Area #52 51st Street"
    timezone = "America/Chicago"
    start_urls = ["https://www.51ststreetchicago.com/about.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        items = response.css("div.paragraph")[3:4]
        titles = items.css("strong::text").getall()
        meetings = items.css("ul")
        items = list(zip(titles, meetings))

        for i, item in enumerate(items):
            for meet in item[1].css("li"):
                meet = self._clean_meet(meet)

                meeting = Meeting(
                    title=self._parse_title(item[0]),
                    description=self._parse_description(item),
                    classification=self._parse_classification(item),
                    start=self._parse_start(meet),
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

    def _replace_meet_chars(self, meet):
        meet = meet.css("::text").get()
        meet = meet.replace(".", "")
        meet = meet.replace("\xa0", "")
        meet = meet.replace("…", "")
        meet = meet.replace(",", "")
        meet = meet.strip()

        return meet

    def _clean_meet(self, meet):
        """Clean and parse a possible meet <li> item"""
        payload = {}
        meet = self._replace_meet_chars(meet)
        meet = meet.split()

        if len(meet) == 4:
            day_week = meet[0]
            month = meet[1]
            month_day = meet[2]
            year = meet[3][:4]
            time = meet[3][4:]
            payload = {
                "day_week": day_week,
                "month": month,
                "month_day": month_day,
                "year": year,
                "time": time,
            }

        if len(meet) == 6:
            day_week = meet[0]
            month = meet[1]
            month_day = meet[2]
            year = meet[3][:4]
            time = meet[3][4:]
            info = " ".join(meet[4:])
            payload = {
                "day_week": day_week,
                "month": month,
                "month_day": month_day,
                "year": year,
                "time": time,
                "info": info,
            }

        return payload

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        item = item.replace("\xa0", "").strip()
        return item

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        months = [
            "JANUARY",
            "FEBRUARY",
            "MARCH",
            "APRIL",
            "MAY",
            "JUNE",
            "JULY",
            "AUGUST",
            "SEPTEMBER",
            "OCTOBER",
            "NOVEMBER",
            "DECEMBER",
        ]

        try:
            date = datetime.strptime(
                f"{item['month_day']} {item['month']}, {item['year']}", "%d %B, %Y"
            )
        except ValueError:
            for month in months:
                ratio = SequenceMatcher(None, month, item["month"]).ratio()
                if ratio > 0.5:
                    date = datetime.strptime(
                        f"{item['month_day']} {month}, {item['year']}", "%d %B, %Y"
                    )

        time = item["time"].split(":")  # [0] = hours, [1] = minutes
        date = date.replace(hour=int(time[0]), minute=int(time[1]))
        return date

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
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
