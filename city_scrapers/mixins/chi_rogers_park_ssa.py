import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting


class ChiRogersParkSsaMixin:
    timezone = "America/Chicago"

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        link_dict = self._parse_links(response)

        for section in response.css(".et_pb_tab_1 p"):
            text_items = section.css("*::text").extract()
            year_str = text_items[0][:4]
            for idx, text_item in enumerate(text_items):
                if not re.search(r"[a-z]{3,10} \d{1,2}", text_item):
                    continue
                start = self._parse_start(text_item.strip(), year_str)
                meeting = Meeting(
                    title=self._parse_title(idx, text_items),
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="See agenda to confirm time",
                    location=self.location,
                    links=link_dict[start],
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, idx, items):
        """Parse or generate meeting title."""
        if "Emergency" in items[idx]:
            return "Emergency Meeting"
        if idx + 1 < len(items) - 1 and "special" in items[idx + 1].lower():
            return "Special Meeting"
        return "Commission"

    def _parse_start(self, date_str, year_str):
        """Parse start datetime as a naive datetime object."""
        date_str = re.search(r"[a-zA-Z]{3,10} \d{1,2}", date_str).group()
        return datetime.combine(
            datetime.strptime("{} {}".format(date_str, year_str), "%B %d %Y").date(),
            self.start_time,
        )

    def _parse_links(self, response):
        """Return a dictionary mapping start datetimes to documents"""
        link_dict = defaultdict(list)
        for section in response.css(".et_pb_tab_1 p, .et_pb_tab_2 p"):
            label_str = section.css("*::text").extract_first()
            if not label_str or ("Minutes" not in label_str and "Agenda" not in label_str):
                continue
            year_str = label_str[:4]
            link_title = "Agenda" if "Agenda" in label_str else "Minutes"
            for link in section.css("a"):
                link_text = link.css("::text").extract_first().strip()
                if not re.match(r"^[a-zA-Z]{3,10} \d{1,2}$", link_text):
                    continue
                start = self._parse_start(link_text, year_str)
                link_dict[start].append({"href": link.attrib["href"], "title": link_title})
        return link_dict

    def _validate_location(self, response):
        pass
