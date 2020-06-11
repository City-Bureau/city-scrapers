import re
from datetime import datetime
from itertools import chain

from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    CANCELLED,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlCriminalJusticeInformationSpider(CityScrapersSpider):
    name = "il_criminal_justice_information"
    agency = "Illinois Criminal Justice Information Authority"
    timezone = "America/Chicago"
    start_urls = ["http://www.icjia.state.il.us/about/overview"]
    location = {
        "name": "Illinois Criminal Justice Information Authority",
        "address": "300 W Adams St, Suite 200, Chicago, IL 60606",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for item in response.css(".panel"):
            desc = self._parse_description(item)
            title = self._parse_title(item)
            classification = self._parse_classification(title)
            location = self._parse_location(desc)
            start_str, end_str = self._parse_time_str(desc)
            exceptions = self._parse_exceptions(item)

            for row in item.css("tbody tr"):
                # Ignore expand/collapse rows
                if len(row.css("td.hiddenRow")) > 0:
                    continue
                row_loc = location
                row_end_str = end_str
                start, asterisks = self._parse_start(row, start_str)
                # Check if asterisks exist and strikethrough not present
                if (
                    asterisks
                    and asterisks in exceptions
                    and len(row.css("strike, s")) < 1
                ):
                    exception = exceptions[asterisks]
                    row_start_str, ex_end_str = self._parse_time_str(exception)
                    if ex_end_str:
                        row_end_str = ex_end_str
                    start = self._parse_start_exception(
                        exception, row_start_str or start_str
                    )
                    row_loc = self._parse_location(exception, default=location)

                if start < last_year and not self.settings.getbool(
                    "CITY_SCRAPERS_ARCHIVE"
                ):
                    continue
                links = self._parse_links(row, response)
                meeting = Meeting(
                    title=title,
                    description="",
                    classification=classification,
                    start=start,
                    end=self._parse_end(start, row_end_str),
                    all_day=False,
                    time_notes="",
                    location=row_loc,
                    links=links,
                    source=response.url,
                )
                # Cancelled if there is a strikethrough and no links present
                if len(row.css("strike, s")) > 0 and len(links) == 0:
                    meeting["status"] = CANCELLED
                else:
                    meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = " ".join(item.css(".panel-heading *::text").extract())
        clean_title = re.sub(r"\s+", " ", title_str).strip()
        return re.search(r"(?<=\d{4}\s).*(?=Meetings)", clean_title).group().strip()

    def _parse_description(self, item):
        """Parse or generate meeting description. Not used in output."""
        desc = item.css(".panel-body > p::text").extract_first()
        if desc:
            return re.sub(r"\s+", " ", desc).strip()

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

    def _parse_start(self, item, time_str):
        """Parse start datetime as a naive datetime object."""
        raw_date_str = " ".join(item.css("td:first-of-type *::text").extract())
        date_str = re.sub(r"\s+", " ", raw_date_str).strip()
        if "rescheduled" in date_str.lower():
            date_str = re.split(r"Rescheduled (to )?", date_str, flags=re.IGNORECASE)[
                -1
            ]
            date_str = date_str.replace("Rescheduled", "").strip()

        asterisks = re.search(r"\*+", date_str)
        if asterisks:
            asterisks = asterisks.group()
            date_str = date_str.replace(asterisks, "")
        start = self._parse_dt_str(date_str, time_str)
        return start, asterisks

    def _parse_end(self, start, time_str):
        """Parse end time if provided"""
        if time_str:
            date_str = start.strftime("%B %d, %Y")
            return self._parse_dt_str(date_str, time_str)

    def _parse_time_str(self, desc):
        """Parse start time from description if available"""
        if desc is None:
            return None, None
        time_match = [
            m
            for m in re.findall(r"\d{1,2}(?:\:\d{1,2})?\s*[apAP][\.mM]{1,3}", desc)
            if m
        ]
        start_str = None
        end_str = None
        if len(time_match) == 1:
            start_str = time_match[0]
        elif len(time_match) == 2:
            start_str, end_str = time_match
        elif len(time_match) == 4:
            start_str = time_match[2]
            end_str = time_match[3]
        # Remove spaces to make parsing more uniform
        if start_str:
            start_str = re.sub(r"[\. ]", "", start_str)
        if end_str:
            end_str = re.sub(r"[\. ]", "", end_str)
        return start_str, end_str

    def _parse_dt_str(self, date_str, time_str):
        # Remove everything after the year
        dt_str = re.search(r".*\d{4}", date_str).group()
        date_fmt = "%B %d, %Y"
        if time_str:
            dt_str = "{} {}".format(dt_str, time_str)
            if ":" in time_str:
                date_fmt += " %I:%M%p"
            else:
                date_fmt += " %I%p"
        return datetime.strptime(dt_str, date_fmt)

    def _parse_location(self, desc, default=location):
        """Parse or generate location."""
        # Split on string used before the location and time
        if not desc or not any(w in desc for w in ["Chicago", "IL", "Illinois"]):
            return default
        split_str = "location: " if "location: " in desc else " at "
        desc_split = desc.split(split_str)
        loc_split = desc_split[-1].split(", ")
        if len(loc_split) < 4:
            name = ""
            address = desc_split[-1].replace(".", "")
        else:
            name = re.sub(r"^the ", "", loc_split[0])
            address = ", ".join(loc_split[1:]).replace(".", "")
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        for link in chain(
            item.css("a"),
            item.xpath(
                "following-sibling::tr[position()=1]//td[contains(@class, 'hiddenRow')]//a"  # noqa
            ),
        ):
            links.append(
                {
                    "title": re.sub(
                        r"\s+", " ", " ".join(link.css("*::text").extract())
                    ).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links

    def _parse_exceptions(self, item):
        """
        Parse any exception with an asterisk, return dictionary of asterisks and text
        """
        exception_map = {}
        desc_items = item.css(".panel-body > p::text").extract()
        if len(desc_items) < 2:
            return exception_map
        for desc in desc_items[1:]:
            clean_desc = re.sub(r"\s+", " ", desc).strip()
            asterisks = re.search(r"^\*+", clean_desc)
            if asterisks:
                asterisk_str = asterisks.group()
                exception_map[asterisk_str] = clean_desc[len(asterisk_str) :].strip()
        return exception_map

    def _parse_start_exception(self, exception, start_str):
        """Parse meeting start time from exception text"""
        date_match = re.findall(r"\w{3,10} \d{1,2}, \d{4}", exception)
        return self._parse_dt_str(date_match[-1], start_str)
