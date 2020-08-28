import html
import json
import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiSsa25Spider(CityScrapersSpider):
    name = "chi_ssa_25"
    agency = "Chicago Special Service Area #25 Little Village"
    timezone = "America/Chicago"
    start_urls = ["https://littlevillagechamber.org/ssa-25/meetings-minutes/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        yield from self._parse_events(response)
        # Only parse one previous page of results in addition to the main page
        for prev_link in response.css("a.tribe-events-c-nav__prev"):
            yield response.follow(prev_link.attrib["href"], callback=self._parse_events)

    def _parse_events(self, response):
        for event_link in response.css(
            "a.tribe-events-calendar-list__event-title-link"
        ):
            yield response.follow(
                event_link.attrib["href"], callback=self._parse_detail
            )

    def _parse_detail(self, response):
        schema_text = response.css(
            "[type='application/ld+json']:not(.yoast-schema-graph)::text"
        ).extract_first()
        if not schema_text:
            return
        schema_data = json.loads(schema_text)[0]
        meeting = Meeting(
            title=schema_data["name"],
            description=self._parse_description(schema_data),
            classification=COMMISSION,
            start=self._parse_dt_str(schema_data["startDate"]),
            end=self._parse_dt_str(schema_data["endDate"]),
            time_notes="",
            all_day=False,
            location=self._parse_location(schema_data),
            links=self._parse_links(response),
            source=schema_data["url"],
        )
        meeting["status"] = self.get_status(meeting)
        meeting["id"] = self.get_id(meeting)

        yield meeting

    def _parse_description(self, item):
        desc_sel = Selector(text=html.unescape(item.get("description", "")))
        return re.sub(
            r"\s+", " ", " ".join(desc_sel.css("*::text").extract()).replace("\\n", "")
        ).strip()

    def _parse_dt_str(self, dt_str):
        return datetime.strptime(dt_str[:-6], "%Y-%m-%dT%H:%M:%S")

    def _parse_location(self, item):
        location = item["location"]
        if "conference call" in location["name"].lower() or "Zoom" in location["name"]:
            return {
                "name": "Conference Call",
                "address": "",
            }
        loc_addr = location["address"]
        addr_str = " ".join(
            [
                loc_addr["streetAddress"],
                f"{loc_addr.get('addressLocality', 'Chicago')}, {loc_addr.get('addressRegion', 'IL')}",  # noqa
                loc_addr["postalCode"],
            ]
        )
        return {"name": location["name"], "address": addr_str}

    def _parse_links(self, response):
        """Parse or generate links"""
        links = []
        for link in response.css("#primary .fl-row-content-wrap a.uabb-button"):
            link_text = " ".join(link.css("*::text").extract())
            if "minutes" in link_text.lower():
                link_title = "Minutes"
            else:
                link_title = link_text.strip()
            links.append(
                {"title": link_title, "href": response.urljoin(link.attrib["href"])}
            )
        return links
