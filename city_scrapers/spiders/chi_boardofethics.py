import re

import dateutil.parser
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiBoardOfEthicsSpider(CityScrapersSpider):
    name = "chi_boardofethics"
    agency = "Chicago Board of Ethics"
    start_urls = ["https://www.chicago.gov/city/en/depts/ethics/supp_info/minutes.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for date_table in response.css(".page-full-description-above .col-xs-12 table"):
            header = (
                date_table.xpath("./preceding-sibling::*")
                .css("h2::text, h3::text")[-1]
                .extract()
            )
            description = re.sub(
                r"\s+",
                " ",
                date_table.xpath("./preceding-sibling::p/text()")[-1].extract() or "",
            )
            location = self._parse_location(description)
            for meeting_date in date_table.css("tbody tr td::text").extract():
                if not meeting_date.strip():
                    continue
                start = self._parse_start(meeting_date, description, header)
                meeting = Meeting(
                    title="Board of Directors",
                    description=description,
                    classification=BOARD,
                    start=start,
                    end=None,
                    time_notes="",
                    all_day=False,
                    location=location,
                    links=self._parse_links(start, response),
                    source=response.url,
                )
                meeting["id"] = self._get_id(meeting)
                meeting["status"] = self._get_status(meeting, text=meeting_date)
                yield meeting

    @staticmethod
    def _parse_start(date_str, description, header):
        """Parse state datetime."""
        header_year_match = re.search(r"\d{4}", header)
        date_year_match = re.search(r"\d{4}", date_str)
        if header_year_match and not date_year_match:
            date_str += ", {}".format(header_year_match.group())
        time_match = re.search(r"(1[0-2]|0?[1-9]):([0-5][0-9])( ?[AP]M)?", description)
        return dateutil.parser.parse("{} {}".format(date_str, time_match.group(0)))

    @staticmethod
    def _parse_location(text):
        name = re.compile(r"(held at the) (?P<name>.*?),(?P<address>.*).")
        matches = name.search(text)
        location_name = matches.group("name").strip()
        address = matches.group("address").strip()
        return {
            "name": location_name,
            "address": address,
        }

    def _parse_links(self, start, response):
        links = []
        for link_el in response.css(
            ".page-full-description a[title$='{}']".format(start.year)
        ):
            if start.strftime("%B") in link_el.xpath("./text()").extract_first():
                links.append(
                    {
                        "title": "Minutes",
                        "href": response.urljoin(
                            link_el.xpath("@href").extract_first()
                        ),
                    }
                )
        return links
