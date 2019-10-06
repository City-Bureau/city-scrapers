import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa18Spider(CityScrapersSpider):
    name = "chi_ssa_18"
    agency = "Chicago Special Service Area #18 North Halsted"
    timezone = "America/Chicago"
    allowed_domains = ["northalsted.com"]
    start_urls = ["https://northalsted.com/community/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".meetings"):
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
        title = item.css(".title::text").get()
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        description = item.css(".page_tagline::text").get()
        return description

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        
        date_str = item.css("*::text").get()
        date_match = re.search(r'\w{3,9} \d{1,2}, \d{4}', date_str)
        if date_match == True:
            date_match_str = date_match.group().replace() # saved for potential typos on website
            parsed_date = datetime.strptime(date_match_str, '%B %d, %Y')
            return datetime.combine(parsed_date.date(), time(14))
        
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
            "address": item.css(".ti_location_pin::text").get(),
            "name": "North Halsted",
        }

    def _parse_links(self, response):
        """Parse or generate links."""
        for link in response.css("p a"):
            link_text = re.sub(r"[\s\t\r]+", " ", link.css("*::text").get())
            dt_match = re.search(
                r"[a-z]+ \d{1,2}, \d{4},? at [\d:o]{4,5} ?[apm\.]{2,4}", link_text, flags=re.I
            )
            if not dt_match:
                dt_str = dt_match.group()
                dt = datetime.strptime(
                    re.sub(r"([\.,]| (?=[pa][\.m]))", "", dt_str.replace("oo", "00")),
                    "%B %d %Y at %I:%M%p"
                )
                
            self.link_map[dt] = [{"title": "Minutes", "href": link.attrib["href"]}]
        
    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
