import re
from collections import defaultdict
from datetime import datetime
from itertools import zip_longest

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


def grouper(n, iterable, fillvalue=None):
    """From itertools recipes"""
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


class IlLaborSpider(CityScrapersSpider):
    name = "il_labor"
    agency = "Illinois Labor Relations Board"
    start_urls = ["https://www2.illinois.gov/ilrb/meetings/Pages/default.aspx"]
    event_timezone = "America/Chicago"
    location = {
        "name": "Room S-401",
        "address": "160 N LaSalle St, Chicago, IL 60602",
    }

    def parse(self, response):
        agenda_map = self._parse_links(response)
        content_lines = response.css(".soi-article-content * *::text").extract()
        clean_lines = [
            re.sub(r"\s+", " ", l).strip() for l in content_lines if l.strip()
        ]
        content = "\n".join(clean_lines)
        meeting_split = re.split(r"^([A-Z ]+)$", content, flags=re.M)
        if not re.match(r"^[A-Z ]+$", meeting_split[0]):
            meeting_split = meeting_split[1:]

        for title_str, item in grouper(2, meeting_split, fillvalue=""):
            title = self._parse_title(title_str)
            start = self._parse_start(item)
            if not start:
                continue
            meeting = Meeting(
                title=title,
                description="",
                classification=BOARD,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(item),
                links=agenda_map[title],
                source=response.url,
            )
            meeting["status"] = self._get_status(
                meeting, text=" ".join([title_str, item])
            )
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, title_str):
        return re.sub(r" meeting$", "", title_str.strip(), flags=re.I).strip().title()

    def _parse_start(self, item):
        """Parse start date and time from item text"""
        date_line = " ".join(item.split("\n")[1:])
        date_match = re.search(r"[A-Z][a-z]{2,8} \d{1,2}", date_line)
        if not date_match:
            return
        year_str = str(datetime.now().year)
        year_match = re.search(r"\d{4}", date_line)
        if year_match:
            year_str = year_match.group()

        date_str = " ".join([date_match.group().replace(",", ""), year_str])
        time_match = re.search(r"\d{1,2}:\d{2} ?[apm\.]{2,4}", item, flags=re.I)
        time_str = "12:00am"
        if time_match:
            time_str = re.sub(r"[ \.]", "", time_match.group())
        return datetime.strptime(" ".join([date_str, time_str]), "%B %d %Y %I:%M%p")

    def _parse_location(self, item):
        addr_matches = re.findall(r"^\d+ .*$", item, flags=re.M | re.DOTALL)
        if "160 N" in item or len(addr_matches) == 0:
            return self.location
        chi_addrs = [a for a in addr_matches if "Chicago" in a]
        if len(chi_addrs) == 0:
            addr_str = addr_matches[0]
        else:
            addr_str = chi_addrs[0]
        return {
            "name": "",
            "address": addr_str.replace(" and").strip(),
        }

    def _parse_links(self, response):
        agenda_map = defaultdict(list)
        for link in response.css(".soi-article-content a"):
            link_title = " ".join(link.css("*::text").extract()).strip()
            meeting_title = self._parse_title(link_title)
            agenda_map[meeting_title].append(
                {"title": "Agenda", "href": response.urljoin(link.attrib["href"])}
            )
        return agenda_map
