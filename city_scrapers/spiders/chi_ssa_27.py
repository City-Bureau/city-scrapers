from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping needs.
        """
        meeting, meeting_location = '', ''

        for item in response.css("#content-232764 div.panel-body p"):

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
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
        yield meeting

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
        item_txt = item.css('a::text').get()
        if not item_txt:
            item_txt = item.css('p::text').get()

        item_txt = item_txt.replace("Annual Meeting", '').replace("Sept", 'Sep')

        p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice after this

        front_str = item_txt[:p_idx]  # remove comments from the rest of the string
        time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
        dt_time_obj = datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')
        return dt_time_obj

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
            if "Sheil Park" in first_note:
                return {
                    "address": "3505 N. Southport Ave., Chicago, IL 60657",
                    "name": "Sheil Park",
                }
            else:
                raise ValueError('Meeting address has changed')

    def _parse_links(self, item):
        """   Parse or generate documents.   """
        url = item.css('a::attr(href)').get()
        if url:
            return [{'href': url, 'title': 'Minutes'}]
        else:
            return []

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
