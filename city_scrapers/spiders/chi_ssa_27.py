import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
""" from pjsier: #we'll want to parse the agenda links from them too.
 We also want to get the separate committee meetings and minutes as well.
 You can get committee meetings and descriptions with div[pageareaid="2"]
 li:last-child p and minutes with div[pageareaid="Sidebar"] li:last-child a
"""

class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]

    # main_page_title = response.css("title::text").get()
    #mySel = response.Selector

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping needs.
        """
        meeting = ''
        meeting_location = ''
        start_time = ''

        panel = "#content-232764 div.panel-body p"
        sel =  response.css(panel)

        for item in response.css(panel):

            if item.css("p > strong ::text").getall():
                meeting_location = self._parse_location(item)
                continue

            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(),
                classification=self._parse_classification(),
                start=self._parse_start(item),
                end=self._parse_end(),  # no indication of such
                all_day=self._parse_all_day(),  # no indication of such
                time_notes=self._parse_time_notes(),  # haven't seen any
                location=meeting_location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )
            print()
            print(str(meeting._values))
            #meeting["status"] = self._get_status(meeting)
            #meeting["id"] = self._get_id(meeting)
        #yield meeting

    # We can just use "Commission" here, but if it's a committee meeting it should
    # return the name of the committee instead.

    def pdf_parse(self, item):
        is_pdf = False

        if item.css('a::attr(href)').get():  # perfect!!!
            is_pdf = True
        #item_txt = item.css("p::text").getall()


        if is_pdf:
            # split datetime from url
            newlist = re.split(r'target=\"_blank">', item)
            date_time = self._parse_start(newlist[1])
            return date_time
        else:
            return False

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        item_txt = ''.join(item.css("p::text").getall())
        if "Annual Meeting" in item_txt:
            return "Annual Meeting"
        else:
            return COMMISSION

    @staticmethod
    def _parse_description():
        """Parse or generate meeting description."""
        # description is used for any descriptions distinct to a single meeting,
        # not a description of the agency so this can be left blank
        return ""

    @staticmethod
    def _parse_classification():
        """Parse or generate classification from allowed options."""
        # This can return COMMISSION generally or COMMITTEE for the committee meetings
        return COMMISSION

    def _parse_start(self, item):
        link = item.css('a::attr(href)').get()  # perfect!!!

        if link:
            print("meeting past")
           # newlist = re.split(r'target=\"_blank">', item)
           # date_time = self._parse_start(newlist[1])
            return 'Past'

        elif not link:  ## not a link so it's upcoming
            start_datetime = None
            return start_datetime

    @staticmethod
    def _parse_end():
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    @staticmethod
    def _parse_time_notes():
        """Parse any additional notes on the timing of the meeting"""
        return ""

    @staticmethod
    def _parse_all_day():
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""

        first_note = item.css("p > strong ::text").get()

        if first_note:
            if  "Sheil Park" in first_note:
                return {
                    "address": "3505 N. Southport Ave., Chicago, IL 60657",
                    "name": "Sheil Park",
                }
            else:
                raise ValueError('Meeting address has changed')

    def _parse_links(self, item):
        """
        Parse or generate documents.
        """
        url = item.css('a::attr(href)').get()      # perfect!!!
        if url:
            return [{'href': url, 'title': 'Minutes'}]
        else:
            return []

    def get_mon(self, month_str):
        months = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        return months[month_str]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
