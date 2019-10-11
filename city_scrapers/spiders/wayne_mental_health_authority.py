import re
from collections import defaultdict
from datetime import datetime

import scrapy
from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class WayneMentalHealthAuthoritySpider(CityScrapersSpider):
    name = "wayne_mental_health_authority"
    agency = "Detroit Wayne Mental Health Authority"
    timezone = "America/Detroit"
    start_urls = ["https://www.dwihn.org/about-us/dwmha-authority-board/board-meeting-documents/"]
    location = {
        "name": "Detroit Wayne Integrated Health Network",
        "address": "707 W Milwaukee Ave, Detroit, MI 48202",
    }

    def __init__(self, *args, **kwargs):
        self.link_map = defaultdict(list)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        self._parse_documents(response)
        yield scrapy.Request(
            "https://www.dwihn.org/about-us/dwmha-authority-board/board-directors-2017-committee-and-board-meeting-schedule/",  # noqa
            callback=self._parse_schedule,
            dont_filter=True
        )

    def _parse_documents(self, response):
        """Parse links from documents page"""
        for link_list in response.css(".left-stage > ul"):
            meeting_title = self._parse_link_meeting_title(link_list.xpath("./li"))
            if not meeting_title:
                continue
            for link_item in link_list.xpath("./ul/li"):
                link_start = self._parse_link_start(link_item)
                if not link_start:
                    continue
                self.link_map[(meeting_title, link_start)].append({
                    "href": link_item.css("a::attr(href)").extract_first(),
                    "title": "Agenda",
                })
                for sub_link in link_item.xpath("./following-sibling::*[1]/li"):
                    self.link_map[(meeting_title, link_start)].append({
                        "href": sub_link.css("a::attr(href)").extract_first(),
                        "title": " ".join(sub_link.css("*::text").extract()),
                    })

    def _parse_schedule(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        title_block = " ".join(response.css(".ccm-layout-8-col-1 *::text").extract())
        year_str = re.search(r"\d{4}", title_block).group()
        for meeting_block in response.css(".ccm-layout-wrapper .ccm-block-styles"):
            title = self._parse_title(meeting_block.xpath("./div[1]"))
            time_str = self._parse_time_str(meeting_block)
            if not title:
                continue

            for item in meeting_block.css("div")[3:]:
                start = self._parse_start(item, year_str, time_str)
                if not start:
                    continue
                meeting_title = self._parse_meeting_title(item)
                if meeting_title:
                    title = meeting_title
                meeting = Meeting(
                    title=title,
                    description="",
                    classification=self._parse_classification(title),
                    start=self._parse_start(item, year_str, time_str),
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self.location,
                    links=self.link_map[(title, start.date())],
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = re.sub(
            r"\s+", " ", " ".join(item.css("*::text").extract()).strip().title().split(" - ")[0]
        ).strip()
        if "Full Board" in title_str:
            return "Board of Directors"
        return title_str.replace("Sud", "SUD")

    def _parse_meeting_title(self, item):
        title_str = re.sub(r"\s+", " ", " ".join(item.css("*::text").extract())).strip()
        if "Committee" not in title_str:
            return
        title_match = re.search(r".*? Committee", title_str)
        if title_match:
            return title_match.group()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "Board of Directors" in title:
            return BOARD
        if "Committee" in title and "Advisory" not in title:
            return COMMITTEE
        return ADVISORY_COMMITTEE

    def _parse_start(self, item, year_str, start_time_str):
        """Parse start datetime as a naive datetime object."""
        item_str = " ".join(item.css("*:not(del)::text").extract())
        date_match = re.search(r"[a-zA-Z]{3,10}\s+\d{1,2}", item_str)
        if not date_match:
            return
        date_str = date_match.group()
        time_match = re.search(r"\d{1,2}(:\d{2})?\s*[apm\. ]{2,6}", item_str)
        if time_match:
            time_str = re.sub(r"[\. ]", "", time_match.group())
        elif start_time_str:
            time_str = start_time_str
        else:
            time_str = "12am"
        if ":" in time_str:
            time_format = "%I:%M%p"
        else:
            time_format = "%I%p"
        return datetime.strptime(
            " ".join([year_str, date_str, time_str]), "%Y %B %d {}".format(time_format)
        )

    def _parse_time_str(self, item):
        """Parse time string from meeting block"""
        title_block = " ".join(item.css("div")[1:3].css("*::text").extract())
        time_match = re.search(r"\d{1,2}(:\d{2})?\s*[apm\. ]{2,6}", title_block)
        if time_match:
            return re.sub(r"[\. ]", "", time_match.group())

    def _parse_link_meeting_title(self, item):
        item_str = re.sub(r"\s+", " ", " ".join(item.css("*::text").extract()).title()).strip()
        if "Full Board" in item_str:
            return "Board of Directors"
        if "Committee" not in item_str:
            return
        return (item_str.split(" Committee")[0] + " Committee").replace("Sud", "SUD")

    def _parse_link_start(self, item):
        item_str = " ".join(item.css("*::text").extract())
        date_match = re.search(r"[a-zA-Z]{3,10}\s+\d{1,2},? \d{4}", item_str)
        if date_match:
            date_str = re.sub(r"\s+", " ", date_match.group().replace(",", "")).strip()
            return datetime.strptime(date_str, "%B %d %Y").date()
