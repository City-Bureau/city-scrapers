import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa25Spider(CityScrapersSpider):
    name = "chi_ssa_25"
    agency = "Chicago Special Service Area #25 Little Village"
    timezone = "America/Chicago"
    start_urls = [
        "http://littlevillagechamber.org/{}-meetings-minutes/".format(
            datetime.now().year
        )
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("table:first-of-type tr:not(:first-child)"):
            start, end = self._parse_start_end(item)
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=COMMISSION,
                start=start,
                end=end,
                time_notes="",
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(response, item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        meeting_type = item.css("td:nth-of-type(4)::text").extract_first()
        return "Commission: {}".format(meeting_type)

    def _parse_start_end(self, item):
        """Parse start and end datetimes"""
        year = datetime.now().year
        date_text = "".join(item.css("td:first-of-type *::text").extract())
        date_str = "{} {}".format(re.search(r".* \d{1,2}", date_text).group(), year)
        time_str = "".join(item.css("td:nth-of-type(2) *::text").extract())
        duration_str = re.sub(r"[APM]{2}", "", time_str)
        am_pm = re.search(r"[APM]{2}", time_str).group()
        start_str, end_str = [s.strip() for s in duration_str.split("–")]
        start = datetime.strptime(
            "{} {}{}".format(date_str, start_str, am_pm), "%B %d %Y %I:%M%p"
        )
        end = datetime.strptime(
            "{} {}{}".format(date_str, end_str, am_pm), "%B %d %Y %I:%M%p"
        )
        return start, end

    def _parse_location(self, item):
        """Parse location from table row"""
        loc_items = item.css("td:nth-of-type(3) *::text").extract()
        loc_name, addr_list = loc_items[0], loc_items[1:]
        # Get ordinal suffix like 'th' or 'nd' to remove excess space later
        loc_ord = [t for t in addr_list if re.match(r"[a-z]{2}", t)]
        addr = " ".join(addr_list)
        for o in loc_ord:
            addr = addr.replace(" " + o, o)
        if "Chicago" not in addr:
            addr += " Chicago, IL"
        addr = re.sub(r"\s+", " ", addr).strip()
        return {"name": loc_name, "address": addr}

    def _parse_links(self, response, item):
        """Parse or generate links"""
        minutes_link = item.css("td:last-of-type a::attr(href)").extract_first()
        if minutes_link:
            return [{"href": response.urljoin(minutes_link), "title": "Minutes"}]
        return []
