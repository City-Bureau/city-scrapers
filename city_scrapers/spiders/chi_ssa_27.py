import re
from datetime import datetime

from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Field, Item


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]
    minutes_list = []
    location = {
        "name": "Sheil Park",
        "address": "3505 N. Southport Ave., Chicago, IL 60657",
    }

    def parse(self, response):
        """   `parse` should always `yield` Meeting items. """
        self.minutes_list = self.get_minutes_panel_items(response)
        self._validate_locations(response)
        commission_path = "div #content-232764 div.panel-body p"

        for item in response.css(commission_path)[1:]:  # main
            title = self._parse_title(item)
            start = self._parse_start(item)

            if not start:
                continue

            links = self._parse_links(item)

            meeting = Meeting(
                title=title,
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=links,
                source=response.url,
            )
            # Include status excluding "rescheduled from" which triggers cancelled
            status_text = " ".join(item.css("*::text").extract())
            if "rescheduled from" in status_text:
                status_text = ""
            meeting["status"] = self._get_status(meeting, text=status_text)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def get_minutes_panel_items(self, response):
        min_list = []

        class Paragraph(Item):
            link = Field()
            date_date = Field()

        panel = response.css("#content-232768 div.panel-body p")[1:]
        paragraphs = panel.css("p")

        last_paragraph = paragraphs[-1].css("*::text").getall()
        if "\xa0" in last_paragraph:
            paragraphs = paragraphs[:-1]

        first_paragraph = paragraphs[0:1].css("*::text").getall()
        if "\xa0" in first_paragraph:
            paragraphs = paragraphs[1:]

        for p in paragraphs:

            href = p.css("a::attr(href)").get()
            tmp_list = p.css("*::text").getall()
            if len(tmp_list) == 0 or not tmp_list[0].strip():
                continue
            date_match = re.search(
                r"[A-Z][a-z]{2,8} \d{1,2},? \d{4}", tmp_list[0].strip()
            )
            if not date_match:
                continue
            date_str = date_match.group().replace(",", "")
            min_list.append(
                Paragraph(
                    link=href, date_date=datetime.strptime(date_str, "%B %d %Y").date()
                )
            )
        return min_list

    def _parse_links(self, item):
        item_txt = " ".join(item.css("*::text").extract()).strip()
        title = (
            "Minutes"  # so far this is all we have, they don't post Agendas in advance
        )
        replacements = {
            "Annual Meeting": "",
            "Sept": "Sep",
            "June": "Jun",
            "am": "AM",
            ".": "",
        }
        for k, v in replacements.items():
            item_txt = item_txt.replace(k, v)
        d_date = "".join(item_txt.split(",")[0:2])
        date_needed = datetime.strptime(d_date, "%b %d %Y").date()

        try:
            matched_meets = list(
                filter(lambda d: d["date_date"] == date_needed, self.minutes_list)
            )
            if len(matched_meets) == 0 or not matched_meets[0]["link"]:
                return []
            matched_meeting = [{"title": title, "href": matched_meets[0]["link"]}]
        except IndexError:
            return []
        return matched_meeting

    def _parse_title(self, item):
        if "Annual Meeting" in "".join(item.css("p::text").getall()):
            return "Annual Meeting"
        return COMMISSION

    def _parse_start(self, item):
        item_txt = " ".join(item.css("*::text").extract()).strip()
        replacements = {
            "Annual Meeting": "",
            "Sept": "Sep",
            "June": "Jun",
            "am": "AM",
            "pm": "PM",
            ".": "",
        }
        for k, v in replacements.items():
            item_txt = item_txt.replace(k, v)
        p_idx = max(item_txt.find("AM"), item_txt.find("PM"), 0) + 2  # so we can slice
        time_str = item_txt[:p_idx]  # strip rest of the string
        try:
            return datetime.strptime(time_str, "%b %d, %Y, %H:%M %p")
        except ValueError:
            return

    def _validate_locations(self, response):
        commission_path = (
            "#content-232764 div.panel-body > p:nth-child(1) > strong::text"
        )
        commission_addy = response.css(commission_path).get()
        if commission_addy.find("Sheil") < 0:  # fail
            raise ValueError("Commission Meeting location has changed")

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "advisory" in title.lower():
            return ADVISORY_COMMITTEE
        if "board" in title.lower():
            return BOARD
        if "committee" in title.lower():
            return COMMITTEE
        if "task force" in title.lower():
            return COMMISSION
        return NOT_CLASSIFIED
