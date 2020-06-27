from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLaborRetirementFundSpider(CityScrapersSpider):
    name = "chi_labor_retirement_fund"
    agency = "Laborers' & Retirement Board Employees' Annuity & Benefit Fund"
    timezone = "America/Chicago"
    start_urls = ["http://www.labfchicago.org/agendas-minutes"]
    location = {
        "address": "321 N Clark St, Chicago, IL",
        "name": "Fund Office",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        description = " ".join(
            response.css(".mainRail .block p:nth-child(1) *::text").extract()
        )
        if "321 N" not in description and "teleconference" not in description:
            raise ValueError("Meeting location has changed")
        for item in response.css(".days"):
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(
                meeting, text=item.css("li:nth-child(3) td::text").extract_first() or ""
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item.css("li:nth-child(3) td::text").extract_first()
        if "special" in title.lower():
            return "Special Meeting"
        return "Retirement Board"

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        cal_date = item.css(".calendar-day::text").extract_first()
        start_time = item.css("li:nth-child(2)::text").extract_first()
        return datetime.strptime(
            "{} {}".format(cal_date, start_time.upper()), "%m/%d/%Y %I:%M %p"
        )

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("li:last-child a"):
            links.append(
                {
                    "href": response.urljoin(link.attrib["href"]),
                    "title": link.xpath("./text()").extract_first(),
                }
            )
        return links
