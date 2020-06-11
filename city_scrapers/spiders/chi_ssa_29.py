import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa29Spider(CityScrapersSpider):
    name = "chi_ssa_29"
    agency = "Chicago Special Service Area #29 2014 West Town"
    timezone = "America/Chicago"
    start_urls = ["http://www.westtownssa.org/transparency/"]
    location = {
        "name": "West Town Chamber of Commerce",
        "address": "1819 W Chicago Ave Chicago, IL 60622",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)
        meeting_dicts = {}
        # Iterate through current meetings, creating dicts of variable values
        for item in response.css(".content_block:first-child div > div > div"):
            meeting_str = item.xpath("./text()").extract_first() or ""
            start = self._parse_start(meeting_str)
            if not start:
                continue
            title = self._parse_title(meeting_str)
            meeting_dicts[start.date()] = {
                "start": start,
                "title": title,
            }
        # Iterate through minutes, adding links to existing meetings or create new ones
        for item in response.css(".content_attachments a"):
            meeting_str = item.css(".pdf_icon::text").extract_first() or ""
            start = self._parse_start(meeting_str)
            if not start:
                continue
            title = self._parse_title(meeting_str)
            links = [{"title": "Minutes", "href": item.attrib["href"]}]
            if start.date() in meeting_dicts:
                meeting_dicts[start.date()]["links"] = links
            else:
                meeting_dicts[start.date()] = {
                    "title": title,
                    "start": start,
                    "links": links,
                }
        for item in meeting_dicts.values():
            meeting = Meeting(
                title=item["title"],
                description="",
                classification=COMMISSION,
                start=item["start"],
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=item.get("links", []),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, meeting_str):
        """Parse or generate meeting title."""
        special_match = re.search(r"(?<=\().*Meeting(?=\))", meeting_str)
        if special_match:
            return special_match.group().strip()
        return "Commission"

    def _parse_start(self, meeting_str):
        """Parse start datetime as a naive datetime object."""
        date_match = re.search(
            r"[a-zA-Z]{3,10} \d{1,2}([a-z]{2})?,? \d{4}", meeting_str
        )
        if date_match:
            date_str = re.sub(r"(,|(?<=\d)[a-z]{2}(?=[, ]))", "", date_match.group())
            date_obj = datetime.strptime(date_str, "%B %d %Y").date()
        else:
            date_match = re.search(
                r"^\d{2}\.\d{2}\.\d{2,4}(?= Minutes$)", meeting_str.strip()
            )
            # Return early if match not found here
            if not date_match:
                return
            date_str = date_match.group()
            dt_fmt = "%m.%d.%Y" if len(date_str) == 10 else "%m.%d.%y"
            date_obj = datetime.strptime(date_str, dt_fmt)
        time_match = re.search(r"\d{1,2}(:\d{2})? ?[apm\.]{2,4}", meeting_str)
        if time_match:
            time_str = re.sub(r"[\s\.]", "", time_match.group())
            time_fmt = "%I:%M%p" if ":" in time_str else "%I%p"
            time_obj = datetime.strptime(time_str, time_fmt).time()
        else:
            time_obj = time(11)
        return datetime.combine(date_obj, time_obj)

    def _validate_location(self, response):
        """Verify that location hasn't changed"""
        if (
            "1819 w"
            not in " ".join(response.css(".events_block div::text").extract()).lower()
        ):
            raise ValueError("Meeting location has changed")
