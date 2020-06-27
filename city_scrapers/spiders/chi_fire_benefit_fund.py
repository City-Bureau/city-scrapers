import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiFireBenefitFundSpider(CityScrapersSpider):
    name = "chi_fire_benefit_fund"
    agency = "Chicago Firemen's Annuity and Benefit Fund"
    timezone = "America/Chicago"
    start_urls = ["http://www.fabf.org/Meetings.html"]
    location = {
        "name": "Fund Office",
        "address": "20 S Clark St, Suite 300, Chicago, IL 60602",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        link_list = self._parse_link_list(response)
        active_tab = response.css(".tab-pane.active .row")

        for idx, col in enumerate(
            active_tab.css(".col-sm-2:nth-child(2), .col-sm-2:nth-child(3)")
        ):
            # Board meetings are in the first column, committee meetings in the second
            is_board = idx == 0
            for date_str in col.css("*::text").extract():
                # Ignore strings that don't have a year in them
                if not re.search(r"\d{4}", date_str):
                    continue
                start = self._parse_start(date_str)
                links = self._parse_links(start, link_list)
                meeting = Meeting(
                    title=self._parse_title(is_board, links),
                    description="",
                    classification=self._parse_classification(is_board),
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="See agenda for meeting time",
                    location=self.location,
                    links=links,
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting
        for item in response.css(".meetings"):
            start = self._parse_start(item)

    def _parse_title(self, is_board, links):
        """Parse or generate meeting title."""
        if is_board:
            return "Retirement Board"
        # Link titles can have committee names in them, return the first match
        for link in links:
            if "invest" in link["title"].lower():
                return "Investment Committee"
            if "legal" in link["title"].lower():
                return "Legal Committee"
            if "legislative" in link["title"].lower():
                return "Legislative Committee"
            if "budget" in link["title"].lower():
                return "Budget Committee"
            if "special" in link["title"].lower():
                return "Special Meeting"
        return "Committee"

    def _parse_classification(self, is_board):
        """Parse or generate classification from allowed options."""
        if is_board:
            return BOARD
        return COMMITTEE

    def _parse_start(self, date_str):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(date_str.strip(), "%B %d, %Y")

    def _parse_link_list(self, response):
        """Compile a list of all links to documents on the page."""
        links = []
        for link in response.css(".tab-pane.active a"):
            # Remove "(Month)" at end of link title
            link_text = re.sub(
                r"\(.*\)", "", " ".join(link.css("*::text").extract())
            ).strip()
            links.append(
                {"title": link_text, "href": response.urljoin(link.attrib["href"])}
            )
        return links

    def _parse_links(self, start, link_list):
        """
        Parse links from link list. All links for meetings have the formatted date in
        the URL
        """
        start_fmts = [start.strftime("%m-%d-%Y"), start.strftime("%m-%d-%y")]
        return [
            link
            for link in link_list
            if any(start_fmt in link["href"] for start_fmt in start_fmts)
        ]
