import re
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiCityCollegeSpider(CityScrapersSpider):
    name = "chi_city_college"
    agency = "City Colleges of Chicago"
    start_urls = [
        "http://www.ccc.edu/events/Pages/default.aspx?dept=Office%20of%20the%20Board%20of%20Trustees",  # noqa
    ]

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for link in response.css(".event-entry .event-title a::attr(href)").extract():
            yield scrapy.Request(
                response.urljoin(link), callback=self.parse_event_page, dont_filter=True
            )

    def parse_event_page(self, response):
        date_str = response.css("#formatDateA::text").extract_first()
        for item in response.css(".page-content table tr"):
            start = self._parse_start(item, date_str)
            title = self._parse_title(item)
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(title),
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(response),
                links=self._parse_links(response),
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting)
            yield meeting

    def _parse_location(self, response):
        """Parse or generate location"""
        loc_parts = [
            re.sub(r"\s+", " ", part).strip()
            for part in response.css(
                "#contact-info .right-col-content .content *::text"
            ).extract()
            if part.strip()
        ]
        return {
            "name": loc_parts[3],
            "address": " ".join(loc_parts[4:]).replace(" ,", ",").strip(),
        }

    def _parse_title(self, item):
        """Parse or generate event title."""
        title = " ".join(
            item.css("th:nth-child(2) *::text, td:nth-child(2) *::text").extract()
        )
        if "board" in title.lower():
            return "Board of Trustees"
        return title.replace("\u200b", "").strip()

    def _parse_start(self, item, date_str):
        """Parse start date and time from item and page date string"""
        # Remove day of week if present
        date_str = re.search(r"[\d/]{8,10}", date_str).group()
        time_str = item.css("th::text, td::text").extract_first().replace(".", "")
        time_str = time_str.replace("noon", "pm").replace("\u200b", "").strip()
        if time_str:
            return datetime.strptime(
                "{} {}".format(date_str, time_str), "%m/%d/%Y %I:%M %p"
            )
        else:
            return datetime.strptime(date_str, "%m/%d/%Y")

    def _parse_classification(self, title):
        if "committee" in title.lower():
            return COMMITTEE
        return BOARD

    def _parse_links(self, response):
        """Returns an array of links if available"""
        links = []
        link_els = response.xpath(
            "//div[contains(@class, 'right-col-block')]/h2[text() = 'Learn More']"
            "/following-sibling::*//a"
        )
        for link_el in link_els:
            links.append(
                {
                    "href": response.urljoin(link_el.attrib["href"]),
                    "title": link_el.xpath("./text()").extract_first(),
                }
            )
        return links
