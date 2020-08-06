import re
from datetime import datetime

from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSchoolCommunityActionCouncilSpider(CityScrapersSpider):
    name = "chi_school_community_action_council"
    agency = "Chicago Public Schools"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.cps.edu/services-and-supports/parent-engagement/community-action-councils-cacs/"  # noqa
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Sets month counter to the current month, passed to parse_start
        # month_counter = datetime.today().month
        month = datetime.today().month
        # Iterates through every month in the year after the current month
        for item in response.css(".smaller-headings .block"):
            source = item.css("a").css("a::attr(href)").extract_first()
            if source and "humboldparkportal.org" in source:
                continue
            if not source:
                source = response.url
            for month_counter in range(month, 13):
                start = self._parse_start(item, month_counter)
                if not start:
                    continue
                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=COMMITTEE,
                    start=start,
                    end=None,
                    time_notes="",
                    all_day=False,
                    location=self._parse_location(item),
                    links=[],
                    source=source,
                )

                meeting["id"] = self._get_id(meeting)
                meeting["status"] = self._get_status(meeting)
                yield meeting

    def _parse_title(self, item):
        """Parse or generate event title."""
        comm_area = " ".join(item.css(".h4-style *::text").extract()).strip()
        return f"{comm_area} Community Action Council"

    @staticmethod
    def parse_weekday(item_text):
        """
        Parses the source material and retrieves the day of the week that
        the meeting occurs.
        """
        day_match = re.search(r"[A-Z][a-z]+day", item_text)
        if not day_match:
            return
        return datetime.strptime(day_match.group(), "%A").weekday()

    @staticmethod
    def parse_time(item_text):
        """
        Parses the source material and retrieves the time that the meeting
        occurs.
        """
        time_match = re.search(r"\d{1,2}(:\d\d)? ?[APMapm\.]{2,4}", item_text)
        if not time_match:
            return
        time_str = re.sub(r"[\s\.]", "", time_match.group().lower())
        time_fmt = "%I%p"
        if ":" in time_str:
            time_fmt = "%I:%M%p"
        return datetime.strptime(time_str, time_fmt).time()

    @staticmethod
    def count_days(weekday, week_count, month_counter):
        """
        Because the source material provides meeting dates on a reoccuring
        schedule, we must use the parsed day from the parse_day function
        """
        today = datetime.today()
        week_counter = 0
        for x in range(1, 31):
            try:
                current_date = datetime(today.year, month_counter, x)
                if current_date.weekday() == weekday:
                    week_counter += 1
                    if week_counter == week_count:
                        return current_date
            except ValueError:
                break

    def _parse_start(self, item, month_counter):
        """
        Parse start date and time.
        Accepts month_counter as an argument from top level parse function
        to iterate through all months in the year.
        """
        item_text = " ".join(item.css("*::text").extract())
        weekday = self.parse_weekday(item_text)
        # Selects first character in the source, usually the week count
        week_num_match = re.search(r"\d[a-z]{2} [A-Z][a-z]+day", item_text)
        if not week_num_match:
            return
        week_count = re.search(r"\d", week_num_match.group()).group()
        meeting_date = self.count_days(weekday, int(week_count), month_counter)
        if not meeting_date:
            return
        return datetime.combine(meeting_date.date(), self.parse_time(item_text))

    def _parse_location(self, item):
        """Parse or generate location."""
        lines = item.css("p *::text").extract()
        for idx, line in enumerate(lines):
            if "Where" in line:
                return {
                    "name": lines[idx + 1].strip(),
                    "address": f"{lines[idx+2].strip()} Chicago, IL",
                }
        return {"name": "", "address": ""}
