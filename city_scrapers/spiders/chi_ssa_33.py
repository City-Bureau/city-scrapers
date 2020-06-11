import re
from collections import defaultdict
from datetime import datetime

import scrapy
from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa33Spider(CityScrapersSpider):
    name = "chi_ssa_33"
    agency = "Chicago Special Service Area #33 Wicker Park/Bucktown"
    timezone = "America/Chicago"
    start_urls = ["http://www.wickerparkbucktown.com/ssa/commission-meetings/"]
    location = {
        "address": "1414 N Ashland Ave Chicago, IL 60622",
        "name": "Chamber Office",
    }

    def __init__(self, *args, **kwargs):
        """Initialize spider document link dict"""
        self.links_map = defaultdict(list)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("#mainContent li a"):
            if ".pdf" in item.attrib["href"]:
                continue
            yield scrapy.Request(item.attrib["href"], callback=self.parse_docs_page)

    def parse_docs_page(self, response):
        start_month_str = self._parse_docs(response)
        if start_month_str:
            yield scrapy.Request(
                (
                    "http://www.wickerparkbucktown.com/index.php?src=events"
                    "&srctype=events_lister_SSA&m={}&y={}"
                ).format(start_month_str[4:], start_month_str[:4]),
                callback=self.parse_events,
            )

    def _parse_docs(self, response):
        start_date_match = re.search(
            r"[a-z]{3,10} \d{1,2},? \d{4}",
            response.css("#mainContent h1::text").extract_first(),
            flags=re.I,
        )
        if not start_date_match:
            return
        start_date_str = start_date_match.group()
        start_date = datetime.strptime(start_date_str.replace(",", ""), "%B %d %Y")
        start_month_str = start_date.strftime("%Y%m")
        for link in response.css("#mainContent h1 + p a"):
            link_text = link.css("*::text").extract_first()
            self.links_map[start_month_str].append(
                {
                    "href": response.urljoin(link.attrib["href"]),
                    "title": "Agenda" if "agenda" in link_text.lower() else "Minutes",
                }
            )
        for link in response.css("#mainContent h3 + p a"):
            self.links_map[start_month_str].append(
                {
                    "href": response.urljoin(link.attrib["href"]),
                    "title": link.css("*::text").extract_first(),
                }
            )
        return start_month_str

    def parse_events(self, response):
        # Parse all events for the month, yield requests to each event detail page
        for item in response.css(".listerItem"):
            title = self._parse_title(item)
            if "commi" not in title.lower():
                continue
            start, end = self._parse_start_end(item)
            classification = self._parse_classification(title)
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=classification,
                start=start,
                end=end,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(start, title),
                source=self._parse_source(item, response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css("h2 a::text").extract_first().replace("(SSA #33)", "").strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return " ".join(item.css(".blurb *::text").extract()).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        return COMMISSION

    def _parse_start_end(self, item):
        """Parse start and end datetimes as naive datetime objects."""
        date_str = item.css(".date::text").extract_first().strip()
        time_str = item.css(".time::text").extract_first().strip()
        start_time_str, end_time_str = time_str.split("-")
        dt_fmt = "%B %d, %Y %I:%M %p"
        return (
            datetime.strptime("{} {}".format(date_str, start_time_str.strip()), dt_fmt),
            datetime.strptime("{} {}".format(date_str, end_time_str.strip()), dt_fmt),
        )

    def _parse_location(self, item):
        """Parse or generate location."""
        loc_dict = {}
        for detail in item.css(".time"):
            detail_label = detail.css(".label::text").extract_first()
            if not detail_label:
                continue
            if "address" in detail_label.lower():
                addr_str = detail.xpath("./text()").extract_first()
                if "Chicago" not in addr_str:
                    addr_str += " Chicago, IL"
                loc_dict["address"] = addr_str
            if "place" in detail_label.lower():
                loc_dict["name"] = detail.xpath("./text()").extract_first()
        if not loc_dict:
            return self.location
        # Fill in blanks for anything missing
        for key in ["address", "name"]:
            if key not in loc_dict:
                loc_dict[key] = ""
        return loc_dict

    def _parse_links(self, start, title):
        """Parse or generate links."""
        start_month_str = start.strftime("%Y%m")
        if "committee" not in title.lower():
            return [
                link
                for link in self.links_map[start_month_str]
                if "committee" not in link["title"].lower()
            ]
        committee_name = re.search(r"[a-zA-Z ]+(?= Committee)", title).group().strip()
        return [
            link
            for link in self.links_map[start_month_str]
            if committee_name in link["title"]
        ]

    def _parse_source(self, item, response):
        """Parse or generate source."""
        return response.urljoin(item.css("h2 a::attr(href)").extract_first())
