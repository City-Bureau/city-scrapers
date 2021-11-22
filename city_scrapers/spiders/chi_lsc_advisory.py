import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLscAdvisorySpider(CityScrapersSpider):
    name = "chi_lsc_advisory"
    agency = "Chicago Local School Council Advisory Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.cps.edu/about/local-school-councils/local-school-council-advisory-board/"  # noqa
    ]
    location = {
        "name": "Garfield Center",
        "address": "2651 W Washington Blvd, Chicago, IL 60612",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        page_content = " ".join(response.css("#main-content p *::text").extract())
        self._validate_location(page_content)

        time_match = re.search(r"\d{1,2}:\d{2}[apm]{2}", page_content)
        if not time_match:
            raise ValueError("Could not find meeting start time")
        time_str = time_match.group()
        year = int(re.search(r"\d{4}-\d{4}", page_content).group().split("-")[0])
        meeting_date_map = defaultdict(list)
        meeting_text_map = defaultdict(list)

        for item in response.css(".rich-text ul")[:1].css("li"):
            start = self._parse_start(item, year, time_str)
            if not start:
                continue
            meeting_text_map[start].append(" ".join(item.css("*::text").extract()))
            meeting_date_map[start].extend(self._parse_links(item, response))

        for start, links in meeting_date_map.items():
            meeting = Meeting(
                title="Advisory Board",
                description="",
                classification=ADVISORY_COMMITTEE,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=links,
                source=response.url,
            )
            meeting["status"] = self._get_status(
                meeting, text=" ".join(meeting_text_map[start])
            )
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_start(self, item, year, time_str):
        item_text = " ".join(item.css("*::text").extract())
        date_match = re.search(r"[A-Z][a-z]{2,8} \d{1,2}", item_text)
        if not date_match:
            return
        start = datetime.strptime(
            " ".join([date_match.group(), time_str, str(year)]), "%B %d %I:%M%p %Y"
        )
        # If the month is before September it's the second half of the school year
        if start.month < 9:
            start = start.replace(year=year + 1)
        return start

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in item.css("a"):
            link_text = " ".join(link.css("*::text").extract())
            if "-" in link_text:
                link_title = link_text.split(" - ")[-1].strip()
            else:
                link_title = link_text.strip()
            links.append(
                {"title": link_title, "href": response.urljoin(link.attrib["href"])}
            )
        return links

    def _validate_location(self, text):
        """Parse or generate location."""
        if "2651" not in text:
            raise ValueError("Meeting location has changed")
