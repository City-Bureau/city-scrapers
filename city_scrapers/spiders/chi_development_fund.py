import re
from datetime import datetime

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiDevelopmentFundSpider(CityScrapersSpider):
    name = "chi_development_fund"
    agency = "Chicago Development Fund"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_developmentfund.html"  # noqa
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().year - 1
        for column in response.css(".col-xs-12 td p"):
            for meeting_str in re.split(r"\<br *\/?\>", column.extract()):
                item = Selector(text=meeting_str)
                start = self._parse_start(item)
                if start is None or (
                    start.year < last_year
                    and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                ):
                    continue
                meeting = Meeting(
                    title=self._parse_title(meeting_str),
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    time_notes="See agenda for time",
                    all_day=False,
                    location={
                        "name": "City Hall",
                        "address": "121 N LaSalle St, Room 1000, Chicago, IL 60602",
                    },
                    source=response.url,
                    links=self._parse_links(item, response),
                )
                meeting["id"] = self._get_id(meeting)
                meeting["status"] = self._get_status(meeting, text=meeting_str)
                yield meeting

    @staticmethod
    def _parse_title(meeting_str):
        if "advisory" in meeting_str.lower():
            return "Advisory Board"
        return "Board of Directors"

    @staticmethod
    def _parse_start(meeting):
        # Not all dates on site a valid dates (e.g. Jan. 2011), so try to parse
        # and return none if not possible
        clean_str = re.sub(r"[\.,]", "", " ".join(meeting.css("*::text").extract()))
        date_str = re.search(r"[a-zA-z]{1,10} \d{1,2} \d{4}", clean_str)
        if not date_str:
            return
        return dateutil.parser.parse(date_str.group())

    def _parse_links(self, item, response):
        links = []
        for link in item.css("a"):
            link_title = link.attrib["title"]
            if "Agenda" in link_title:
                link_title = "Agenda"
            links.append(
                {"title": link_title, "href": response.urljoin(link.attrib["href"])}
            )
        return links
