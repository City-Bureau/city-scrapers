import html
import json
import re
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE, COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta
from scrapy import Request, Selector


class ChiSsa60Spider(CityScrapersSpider):
    name = "chi_ssa_60"
    agency = "Chicago Special Service Area #60 Albany Park"
    timezone = "America/Chicago"
    months_backward = 6
    months_forward = 3

    def start_requests(self):
        requests = []
        for i in range(-self.months_backward, self.months_forward + 1):
            dt = datetime.strftime(
                datetime.now().date() + relativedelta(months=i), "%Y-%m"
            )
            requests.append(
                Request(
                    "https://northrivercommission.org/events/{}/".format(dt),
                    callback=self.parse,
                )
            )
        return requests

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        json_text = response.xpath(
            "//script[@type='application/ld+json']/text()"
        ).extract()
        if not json_text:
            return
        event_list = []
        for json_str in json_text:
            json_items = json.loads(self._clean(json_str))
            if isinstance(json_items, list):
                event_list.extend(json_items)

        for item in event_list:
            title = self._parse_title(item)
            if title is None:
                continue

            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(title),
                start=self._parse_time(item, "startDate"),
                end=self._parse_time(item, "endDate"),
                all_day=False,  # Found no events of interest scheduled for all day
                time_notes="",
                location=self._parse_location(item),
                links=list(),
                source=item["url"],
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        allowed = ["meeting", "committee", "advisory council"]
        if not any(
            [a in item["name"].lower() for a in allowed]
        ):  # Not a meeting type we want
            return None
        return item["name"]

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        desc_text = " ".join(
            Selector(text=html.unescape(item["description"])).css("*::text").extract()
        )
        return re.sub(r"\s+", " ", desc_text).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        title = title.lower()
        if "advisory" in title:
            return ADVISORY_COMMITTEE
        elif "committee" in title:
            return COMMITTEE
        else:
            return COMMISSION

    def _parse_time(self, item, index):
        # index must be either 'startDate' or 'endDate'
        return datetime.strptime(item[index][:-6], "%Y-%m-%dT%H:%M:%S")

    def _parse_location(self, item):
        """Parse or generate location."""
        name = item["location"]["name"]
        addr_dict = item["location"]["address"]
        street = addr_dict["streetAddress"]
        city = addr_dict["addressLocality"]
        state = addr_dict["addressRegion"]
        zipcode = addr_dict["postalCode"]
        return {
            "address": "{} {}, {} {}".format(street, city, state, zipcode),
            "name": name,
        }

    def _clean(self, inp_str):
        """Replace certain HTML entities"""
        # Couldn't use `html.unescape()` because it replaced quotes and broke JSON
        return (
            inp_str.replace("&#8211;", "-")
            .replace("&#8217;", "'")
            .replace("&#038;", "&")
        )
