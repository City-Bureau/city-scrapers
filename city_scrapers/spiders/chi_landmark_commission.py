import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, FORUM
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
        for header in response.css(".page-center h3"):
            header_text = header.css("*::text").extract_first()
            if "Hearings" in header_text:
                yield from self._parse_hearings(response, header)

            year_match = re.search(r"\d{4}", header_text)
            if not year_match:
                continue
            year_str = year_match.group()
            last_year = datetime.today().year - 1
            if int(year_str) < last_year and not self.settings.getbool(
                "CITY_SCRAPERS_ARCHIVE"
            ):
                continue
            if "Schedule" in header_text:
                yield from self._parse_schedule(response, header, year_str)

    def _parse_schedule(self, response, header, year_str):
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

    def _parse_hearings(self, response, header):
        for paragraph in header.xpath("./following-sibling::p"):
            if len(paragraph.css("strong")) < 1:
                continue
            start = self._parse_hearing_start(paragraph)
            if not start:
                continue
            meeting = Meeting(
                title="Public Hearing",
                description="",
                classification=FORUM,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self.location,
                links=self._parse_hearing_links(response, header),
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(
                meeting, text=" ".join(paragraph.css("*::text").extract())
            )
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

    def _parse_hearing_start(self, item):
        dt_str = re.sub(
            r"[\.,]",
            "",
            " ".join(item.css("strong::text").extract()).split("-")[0].strip(),
        )
        time_fmt = "%I %p"
        if ":" in dt_str:
            time_fmt = "%I:%M %p"
        try:
            return datetime.strptime(dt_str, f"%b %d %Y {time_fmt}")
        except ValueError:
            return datetime.strptime(dt_str, f"%B %d %Y {time_fmt}")

    def _parse_hearing_links(self, response, header):
        links = []
        for link in header.xpath("./following-sibling::*").css("a"):
            if "mailto" in link.attrib["href"]:
                continue
            link_title = " ".join(link.css("*::text").extract()).strip()
            if "title" in link.attrib:
                link_title = link.attrib["title"]
            links.append(
                {"title": link_title, "href": response.urljoin(link.attrib["href"])}
            )
        return links

    def _validate_location(self, response):
        desc_str = " ".join(response.css(".col-xs-12 p::text").extract())
        if "201-A" not in desc_str:
            raise ValueError("Meeting location has changed")
