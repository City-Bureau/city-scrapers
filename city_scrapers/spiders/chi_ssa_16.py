import datetime
import re

from city_scrapers_core.constants import *
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa16Spider(CityScrapersSpider):
    name = "chi_ssa_16"
    agency = "Chicago Special Service Area #16"
    timezone = "America/Chicago"
    start_urls = ["https://greektownchicago.org/about/ssa-16/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Meeting entries are contained in a list item without any specific class or id designation.
        # Because of this, I filtered the present list items on the page with the ", 20" string (every meeting li has this in the present text from the year listed),
        # which indicates the meeting occurred or is scheduled to occur and therefore contains relevant information to document.


        for item in response.xpath('//li[contains(text(), ", 20")]'):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
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


    def _parse_title(self, item):
        """Parse or generate meeting title."""
        # There was no variation in types of meetings, so this was applicable for all.
        return "Greektown Special Service Area Tax Commission #16 Public Meeting"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        # This extracts the useful text provide to describe the services provided by the SSA.
        return " ".join(item.xpath('//span[text()="Improving the Community"]/parent::h4/parent::div/p/text()').extract())

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        # Extracted all alphanumeric characters from the text of each meeting, which contained the dates of the meeting, then split into list containing M, D, Y
        date = re.sub(r"[^a-zA-Z0-9]+", " ", item.xpath("text()").get()).split()
        
        # Extracted just alphabetical characters from month, then used built-in strptime function in datetime to parse numeric month from string
        month = re.sub(r"[^a-zA-Z]+", " ", date[0])
        month = datetime.datetime.strptime(month, "%B").month

        # Extracted numbers from day and year entries of date list to remove any errant characters (i.e. one entry said January 28th where all others read January 28).
        day = int(re.sub(r"[^0-9]+", " ", date[1]))
        year = int(re.sub(r"[^0-9]+", " ", date[2]))

        # According to accompying information, all meetings in 2016 occurred at 3:00 PM, while consequent years occurred at 2:00 PM.
        if (year == 2016):
            return datetime.datetime(year, month, day, 15, 0)
        return datetime.datetime(year, month, day, 14, 0)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        # Meeting adjournment information contained in files present in Minutes documents attached to each meeting that are un-optimized scanned docs.
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        # No other details present
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        # Meetings occurred at same location for all years documented
        return {
            "address": "306 S. Halsted St, 2nd Floor, Chicago, ILL 60661",
            "name": "SSA #16 Office",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        # Most entries contained a Minutes document, but some not yet posted or otherwise have not occurred. When no anchor tag found, returns empty JSON element.
        if (item.xpath("a/@href").get() == None):
            return [{"href": "", "title": ""}]

        return [{"href": item.xpath("a/@href").get(), "title": item.xpath("a/text()").get()}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
