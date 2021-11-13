import datetime
import re

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from w3lib.html import remove_tags


class ChiDesignSpider(CityScrapersSpider):
    name = "chi_design"
    agency = "Chicgo committee on Design"
    timezone = "America/Chicago"
    start_urls = ["https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting_links = self._get_meeting_links(response)
        yield from response.follow_all(meeting_links,
                                       callback=self.parse_meeting)

    def parse_meeting(self, response):
        descriptions = response.css("td:nth-child(2) p::text").getall()
        locations = response.css("td:nth-child(1) p").getall()

        for description, location in zip(descriptions, locations):
            meeting = Meeting(
                title="Committee on Design",
                description=description,
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(response),
                end=self._parse_end(response),
                all_day=self._parse_all_day(response),
                time_notes=self._parse_time_notes(response),
                location=self._parse_location(location),
                links=self._parse_links(response),
                source=self._parse_source(response),
            )
            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            yield meeting

    def _get_meeting_links(self, response):
        meetings = response.css("td p a")
        meeting_links = [link for link in meetings if link.css("::text").get() == "Agenda"]
        return meeting_links

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        year_month_string = response.css(".page-heading::text").get()

        day_time_string = response.css(".col-12 > p:nth-child(1)").get()
        day_time_string = remove_tags(day_time_string)

        return DateTimeFormatter.get_datetime_object(year_string=year_month_string,
                                                     month_string=year_month_string,
                                                     day_string=day_time_string,
                                                     time_string=day_time_string)

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
        item = item.lstrip("<p>")
        item = item.rstrip("</p>")
        item = item.replace("<br>", "")
        return {
            "address": item,
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url


class DateTimeFormatter:
    @classmethod
    def get_datetime_object(cls, year_string, month_string, day_string, time_string):
        year = cls._get_year(year_string)
        month = cls._get_month(month_string)
        day = cls._get_day(day_string)
        hour, minute, am_pm = cls._get_time(time_string)
        return cls._date_time_format(year, month, day, hour, minute, am_pm)

    @staticmethod
    def _get_year(string):
        year_re = r"\b(\d{4})\b"
        year, = re.search(year_re, string).groups(0)
        return year

    @staticmethod
    def _get_month(string):
        month_list = ['january',
                      'february'
                      'march',
                      'april',
                      'may',
                      'june',
                      'july',
                      'august',
                      'september',
                      'october',
                      'november',
                      'december', ]
        string = string.lower()
        for month in month_list:
            if string.find(month) != -1:
                return month.capitalize()

    @classmethod
    def _get_day(cls, string):
        day_re = r"\b\w+\.? (\d{1,2})[,\.]"
        day, = re.search(day_re, string).groups(0)
        return cls._pad_with_a_zero(day)

    @classmethod
    def _get_time(cls, string):
        time_re = re.compile("(\d{1,2})(?::(\d{1,2}))? (am|pm)", re.IGNORECASE)
        result = time_re.search(string)
        hour, minute, am_pm = result.groups()
        hour = cls._pad_with_a_zero(hour)
        if not minute:
            minute = "00"
        return hour, minute, am_pm.lower()

    @staticmethod
    def _date_time_format(year, month, day, hour, minute, am_pm):
        date_string = f"{year}:{month}:{day}:{hour}:{minute}"
        date_time_obj = datetime.datetime.strptime(date_string, "%Y:%B:%d:%H:%M")
        if am_pm == "pm":
            return date_time_obj + datetime.timedelta(hours=12)
        return date_time_obj

    @staticmethod
    def _pad_with_a_zero(string):
        if len(string) == 2:
            return string
        else:
            return "0" + string
