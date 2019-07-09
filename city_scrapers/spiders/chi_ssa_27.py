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
        # You can use ' ' .join(item.css('*::text').extract())
        # content-232764 > div:nth-child(1) > div:nth-child(2)
        ##This can likely be removed and replaced with just checking for links, and then checking if the
        # href attribute ends with .pdf. Something like link.attrib['href'].endswith('.pdf'). You can also extract the
        # href attribute with a CSS selector to do something like item.css('a::attr(href)')
        # to get all of the href attributes of child links
        the_address = ""
        meeting_list = []
        meeting = ''
        meeting_location = ''
        item_hrf = ""
        item_txt = ""
        start_time = ''
        
        for item in response.css("#content-232764 div.panel-body p"):
            item_strong = item.css("p > strong ::text").getall()
            if item_strong:
                meeting_location = self._parse_location(item_strong[0])
                continue
            else:
                item_hrf = item.css('a::attr(href)').get()   #perfect!!!
                item_hrf = item_hrf
                # if not item_hrf.endswith('.pdf'):
                #     item_txt = item.css("p::text").getall()

            if not item_hrf:   ## not a link so it's upcoming
                start_time = self._parse_start(item)

            elif item_hrf:
                print("meeting past")
                item_txt = 'Past'

            if item_hrf or item_txt:
                meeting_list.append([item_hrf, item_txt])
                #else:


            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(),
                classification=self._parse_classification(),
                start=start_time,
                end=self._parse_end(),  # no indication of such
                all_day=self._parse_all_day(),  # no indication of such
                time_notes=self._parse_time_notes(),  # haven't seen any
                location=meeting_location,
                links=[self.item_hrf],
                source=item_hrf,
            )
            print()
            #meeting["status"] = self._get_status(meeting)
            #meeting["id"] = self._get_id(meeting)
        #yield meeting

    # We can just use "Commission" here, but if it's a committee meeting it should
    # return the name of the committee instead.

    def pdf_parse(self, item):
        is_pdf = False

        if item.css('a::attr(href)').get():  # perfect!!!
            is_pdf = True
        item_txt = item.css("p::text").getall()


        if is_pdf:
            # split datetime from url
            newlist = re.split(r'target=\"_blank">', item)
            date_time = self._parse_start(newlist[1])
            return date_time
        else:
            return False

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        item_txt = ''
        item_txt = item.css("p::text").getall()
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
        start_datetime = None
        mon_to_digit = {
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

        item_elems = item.split()
        if not item_elems[0].startswith('Annual', 0, 7):
            month_str = item_elems[0][0:3].lower().rstrip(',')
            month_digit = mon_to_digit[month_str]
            yr = int(item_elems[2].rstrip(','))
            day = int(item_elems[1].rstrip(','))
            tm = item_elems[3].rstrip(',')
            hr = int(tm[0:2].rstrip(':'))
            minit = int(tm[2:4])
            start_datetime = datetime(yr, month_digit, day, hr, minit)
            """
            Parse start datetime as a naive datetime object.
            """
            # This should use the datetime.strptime function

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
        if  "Sheil Park" in item:
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
        url = item.xpath('a/@href').extract_first()
        if url:
            return [{'href': url, 'title': 'Minutes'}]
        return []



    # @staticmethod
    # def _parse_links(item):
    #     """Parse or generate links."""
    #     return [{"href": "", "title": ""}]

    # def _parse_source(self, response):
    #     """Parse or generate source."""
    #     return response.url
