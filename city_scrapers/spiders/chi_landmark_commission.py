import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiLandmarkCommissionSpider(CityScrapersSpider):
    name = "chi_landmark_commission"
    agency = "Commission on Chicago Landmarks"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/dcd/supp_info/landmarks_commission.html"
    ]
    location = {
        "name": "City Hall",
        "address": "121 N LaSalle St, Room 201A, Chicago, IL 60602",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)

        # Only parse the first few sections to avoid returning the whole archive
        for header in response.css(".page-full-description h3")[:3]:
            header_text = header.css("*::text").extract_first()
            if "Schedule" not in header_text:
                continue
            year_str = re.search(r"\d{4}", header_text).group()
            for column in header.xpath("./following-sibling::table[1]").css("td"):
                # Use the immediate child p element instead of the td el if it exists
                if len(column.css("p")) > 0:
                    column = column.css("p")[0]
                # Because the markup is irregular and based on br tags, split the HTML
                # content on br tags and then create separate selectors for each one
                column_str = column.extract()
                if isinstance(column_str, list):
                    column_str = " ".join(column_str)
                for item_str in re.split(r"\<br[\s\/]*?\>", column_str):
                    item = Selector(text=re.sub(r"\s+", " ", item_str).strip())
                    start = self._parse_start(item, year_str)
                    if not start:
                        continue
                    meeting = Meeting(
                        title="Commission",
                        description="",
                        classification=COMMISSION,
                        start=start,
                        end=None,
                        time_notes="See details to confirm time",
                        all_day=False,
                        location=self.location,
                        links=self._parse_links(item, response),
                        source=response.url,
                    )
                    meeting["id"] = self._get_id(meeting)
                    meeting["status"] = self._get_status(meeting, text=item_str)
                    yield meeting

    @staticmethod
    def _parse_start(item, year_str):
        start_match = re.search(
            r"[A-Z][a-z]{2,8}\.? \d{1,2}", " ".join(item.css("*::text").extract())
        )
        if not start_match:
            return
        start_str = start_match.group().replace(".", "")
        # Try multiple month formats
        try:
            return datetime.strptime(
                " ".join([start_str, year_str, "12:45"]), "%B %d %Y %H:%M"
            )
        except ValueError:
            return datetime.strptime(
                " ".join([start_str.replace("Sept", "Sep"), year_str, "12:45"]),
                "%b %d %Y %H:%M",
            )

    @staticmethod
    def _parse_links(item, response):
        links = []
        for link in item.css("a"):
            link_title = " ".join(link.css("*::text").extract()).strip()
            links.append(
                {"title": link_title, "href": response.urljoin(link.attrib["href"])}
            )
        return links

    def _validate_location(self, response):
        desc_str = " ".join(response.css(".col-xs-12 p::text").extract())
        if "201-A" not in desc_str:
            raise ValueError("Meeting location has changed")
