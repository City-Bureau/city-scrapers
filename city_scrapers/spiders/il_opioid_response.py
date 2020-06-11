import re
from datetime import datetime, time

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlOpioidResponseSpider(CityScrapersSpider):
    name = "il_opioid_response"
    agency = "Illinois Opioid Crisis Response Advisory Council"
    timezone = "America/Chicago"
    start_urls = ["https://www.dhs.state.il.us/page.aspx?item=104682"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        for item in response.xpath("//p//a"):
            if "Agenda" not in item.xpath("text()").get():
                break

            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item, response),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Advisory Council"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_match = self._get_date(item)
        if date_match:
            start_date = datetime.strptime(date_match.group(0), "%m.%d.%y")
            return datetime.combine(start_date, time(13))
        else:
            return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        date_match = self._get_date(item)
        if date_match:
            end_date = datetime.strptime(date_match.group(0), "%m.%d.%y")
            return datetime.combine(end_date, time(15))
        else:
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
            "address": "401 S. Clinton Street, 7th Floor Executive Conference Room,"
            " Chicago, IL 60607",
            "name": "Illinois Department of Human Services Clinton Building",
        }

    def _parse_links(self, item, response):
        """Parse or generate links for meeting agenda and minutes."""
        links = []
        agenda = {
            "href": response.urljoin(item.xpath("@href").get()),
            "title": item.xpath("text()").get(),
        }

        links.append(agenda)

        date_match = self._get_date(item)

        if date_match:

            datestr = date_match.group(0)
            date_indices = [
                i
                for i, x in enumerate(response.xpath("//p//a/text()").getall())
                if datestr in x
            ]

            if len(date_indices) > 1:
                minutes_idx = date_indices[1]
                minutes = response.xpath("//p//a")[minutes_idx]

                if datestr in minutes.get():

                    minutes = {
                        "href": response.urljoin(minutes.xpath("@href").get()),
                        "title": minutes.xpath("text()").get(),
                    }

                    links.append(minutes)

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _get_date(self, item):
        text_str = item.xpath("text()").get()
        date_match = re.search(r"\d*\.\d*\.\d*", text_str)
        return date_match
