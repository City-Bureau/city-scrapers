import re
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class IlPublicHealthSpider(CityScrapersSpider):
    name = "il_public_health"
    agency = "Illinois Department of Public Health"
    timezone = "America/Chicago"
    allowed_domains = ["www.dph.illinois.gov"]

    @property
    def start_urls(self):
        """Get all meetings from one year ago through one year in the future"""
        today = datetime.now()
        url_list = []
        for months_diff in range(-12, 13):
            month_str = (today + relativedelta(months=months_diff)).strftime("%Y%m")
            url_list.append("http://www.dph.illinois.gov/events/" + month_str)
        return url_list

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("tr.eventspage"):
            title = self._parse_title(item)
            description = self._parse_description(item)
            # Skip meetings in certain categories
            if self.should_ignore_meeting(title, description):
                continue
            meeting = Meeting(
                title=title,
                description=description,
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location=self._parse_location(description),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(
                meeting, text=item.css(".event_cancelled::text").extract_first() or ""
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css("div.eventtitle::text").extract_first().strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return "\n".join([
            re.sub(r"\s+", " ", line).strip()
            for line in item.css(".event_description > p *::text").extract()
        ])

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_str = item.css(".date-display-single::attr(content)").extract_first()
        return datetime.strptime(start_str[:19], "%Y-%m-%dT%H:%M:%S")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end_el = item.css(".start_end_time .date-display-single:not(:first-child):last-child")
        if end_el:
            end_date = datetime.strptime(end_el.attrib["content"][:19], "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(
                end_el.xpath("./text()").extract_first().strip(), "%I:%M%p"
            ).time()
            return end_date.replace(hour=end_time.hour, minute=end_time.minute)
        end_dt_str = item.css(".date-display-end::attr(content)").extract_first()
        if end_dt_str:
            return datetime.strptime(end_dt_str[:19], "%Y-%m-%dT%H:%M:%S")

    def _parse_location(self, description):
        """Parse or generate location."""
        addr_str = ""
        chi_match = re.search(
            r"(\d{1,5}\s+[^(IL)]{0,150}?Chicago(,\s+IL(\s+\d{5})?)?)",
            description,
            flags=re.DOTALL | re.M
        )
        springfield_match = re.search(
            r"(\d{1,5}\s+[^(IL)]{0,150}?Springfield(,\s+IL(\s+\d{5})?)?)",
            description,
            flags=re.DOTALL | re.M
        )
        il_match = re.search(
            r"(\d{1,5}\s+.{0,150}?IL(\s+\d{5})?)", description, flags=re.DOTALL | re.M
        )
        if chi_match:
            addr_str = chi_match.group()
        elif springfield_match:
            addr_str = springfield_match.group()
        elif il_match:
            addr_str = il_match.group()
        if addr_str and "IL" not in addr_str:
            addr_str += ", IL"
        return {
            "address": re.sub(r"\n+", "\n", addr_str).strip(),
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for link in item.css(".addl_materials a, .meeting_minutes_agenda a"):
            links.append({
                "title": link.xpath("./text()").extract_first(),
                "href": link.attrib["href"],
            })
        return links

    def should_ignore_meeting(self, title, description):
        return any(
            p in " ".join([title.lower(), description.lower()])
            for p in ["training session", "symposium", "workshop"]
        )
