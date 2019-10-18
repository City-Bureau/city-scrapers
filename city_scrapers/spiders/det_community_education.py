import json
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.http import HtmlResponse


class DetCommunityEducationSpider(CityScrapersSpider):
    name = "det_community_education"
    agency = "Detroit Community Education Commission"
    timezone = "America/Detroit"
    start_urls = [
        "https://cecdetroit.org/wp-json/tribe/events/v1/events?start_date=2018-01-01&per_page=100"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        res = json.loads(response.text)
        for item in res["events"]:
            # Ignore webinars
            if "webinar" in item["title"].lower():
                continue
            meeting = Meeting(
                title=item["title"].strip(),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=item["url"],
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(item["start_date"], "%Y-%m-%d %H:%M:%S")

    def _parse_classification(self, item):
        """Parse classification from item title"""
        if any(
            p in item["title"].lower()
            for p in ["info session", "community event", "community meeting"]
        ):
            return FORUM
        return COMMISSION

    def _parse_location(self, item):
        """Parse or generate location."""
        venue = item["venue"]
        return {
            "name": venue["venue"],
            "address":
                " ".join([venue[a] for a in ["address", "city", "state", "zip"] if a in venue])
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        res = HtmlResponse(url=item["url"], body=item["description"], encoding="utf-8")
        links = []
        for link in res.css("a"):
            link_href = res.urljoin(link.attrib["href"])
            link_title = " ".join(link.css("* ::text").extract()).strip()
            if "viewform" not in link_href and link_title:
                links.append({"href": link_href, "title": link_title})
        return links
