import json
import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookHousingSpider(CityScrapersSpider):
    name = "cook_housing"
    agency = "Cook County Housing Authority"
    timezone = "America/Chicago"
    start_urls = ["http://thehacc.org/about/"]
    location = {
        "name": "HACC Central Office Board Room",
        "address": "175 West Jackson, Suite 350, Chicago, IL 60604",
    }

    def parse(self, response):
        self.link_date_map = defaultdict(list)
        for link in response.css(".additional-resources li a"):
            link_title = re.sub(
                r"\s+", " ", " ".join(link.css("*::text").extract()).strip()
            )
            date_match = re.search(
                r"[a-zA-Z]{3,10} \d{1,2}([a-z]{2})?,? \d{4}", link_title
            )
            if not date_match:
                continue
            date_str = re.sub(r"((?<=\d)[a-z]+|,)", "", date_match.group())
            link_date = datetime.strptime(date_str, "%B %d %Y").date()
            if "agenda" in link_title.lower():
                link_title = "Agenda"
            elif "minutes" in link_title.lower():
                link_title = "Minutes"
            self.link_date_map[link_date].append(
                {"title": link_title, "href": response.urljoin(link.attrib["href"])}
            )

        now = datetime.now()
        for months_delta in range(-2, 3):
            month_str = (now + relativedelta(months=months_delta)).strftime("%Y-%m")
            yield response.follow(
                "/events/{}/".format(month_str), callback=self._parse_events
            )

    def _parse_events(self, response):
        for link in response.css(".item-wrapper .info a"):
            link_text = " ".join(link.css("*::text").extract()).lower()
            if "board" in link_text or "committee" in link_text:
                yield response.follow(link.attrib["href"], callback=self._parse_detail)

    def _parse_detail(self, response):
        schema_text = response.css(
            "script[type='application/ld+json']::text"
        ).extract()[-1]
        schema_json = json.loads(schema_text)
        if isinstance(schema_json, list):
            item = schema_json[0]
        else:
            item = schema_json

        start = self._parse_dt(item["startDate"])
        title = self._parse_title(item["name"])
        meeting = Meeting(
            title=title,
            description="",
            classification=self._parse_classification(title),
            start=start,
            end=self._parse_dt(item["endDate"]),
            all_day=False,
            time_notes="",
            location=self._parse_location(item),
            links=self.link_date_map[start.date()],
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting, text=schema_text)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    @staticmethod
    def _parse_title(title):
        """Parse or generate meeting title."""
        if "board meeting" in title.lower():
            return "Board of Commissioners"
        return title

    @staticmethod
    def _parse_classification(title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        return BOARD

    @staticmethod
    def _parse_dt(dt_str):
        """Parse start and end datetimes as a naive datetime object."""
        return datetime.strptime(dt_str[:-6], "%Y-%m-%dT%H:%M:%S")

    def _parse_location(self, item):
        """Parse or generate location."""
        if not item.get("location"):
            return {
                "name": "TBD",
                "address": "",
            }

        loc_obj = {
            "name": item["location"]["name"],
            "address": "",
        }
        if item["location"].get("address"):
            loc_obj["address"] = " ".join(
                [
                    item["location"]["address"].get(p)
                    for p in [
                        "streetAddress",
                        "addressLocality",
                        "addressRegion",
                        "postalCode",
                    ]
                    if item["location"]["address"].get(p)
                ]
            )
        if "175 W" in loc_obj["address"]:
            return self.location
        return loc_obj
