import re
from datetime import datetime, date, time

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
            meeting["status"] = self._get_status(meeting)
            #meeting["id"] = self._get_id(meeting)
            meeting["id"] = ''
        yield meeting

    # We can just use "Commission" here, but if it's a committee meeting it should
    # return the name of the committee instead.

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
        link_txt = item.css('a::text').get()  # perfect!!!

        if link:
            print("meeting past")
            itmlist = link_txt.split(' ')
            month_str = itmlist[0].lower().rstrip('.')
            month_digit = int(self.get_mon(month_str))
            day = int(itmlist[1].rstrip(','))
            yr = int(itmlist[2].rstrip(','))
            tm = itmlist[3].rstrip(',')
            hr = int(tm[0:2].rstrip(':'))
            minit = int(tm[2:5].rstrip(' '))
            ampm = itmlist[4].rstrip(',')

            date1 = datetime(yr, month_digit, day)
            time_obj = time(hr, minit)
            dt_obj = datetime.combine(date1, time_obj)
            return dt_obj

        elif not link:  ## not a link so it's upcoming
            st_datetime = None
            item_str = item.css('p::text').get()  # perfect!!!
            if not item_str[0].startswith('Annual', 0, 7):
                month_str = item_str[0][0:3].lower().rstrip(',')
                month_digit = self.get_mon(month_str)
                yr = int(item_str[2].rstrip(','))
                day = int(item_str[1].rstrip(','))
                tm = item_str[3].rstrip(',')
                hr = int(tm[0:2].rstrip(':'))
                minit = int(tm[2:4])
                ampm = item_str[4].rstrip(',')

                date1 = datetime(yr, month_digit, day)
                time_obj = time(hr, minit)

                #
                # date_obj = datetime.strptime(st_datetime, "%B %d %Y").date()
                #
                # time_fmt = "%I:%M%p" if ":" in time_obj else "%I%p"
                # time_obj = datetime.strptime(time_obj, time_fmt).time()
            dt_obj = datetime.combine(date1, time_obj)
            return dt_obj



    @staticmethod
    def _parse_end():
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    @staticmethod
    def _parse_time_notes():
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""

        first_note = item.css("p > strong ::text").get()

        if item.css("p > strong ::text").get():
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

    def get_mon(self, mon_int):
        month = {
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
        return month[mon_int]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
