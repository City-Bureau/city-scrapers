import re
from datetime import timedelta

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse


class ChiAnimalSpider(CityScrapersSpider):
    name = "chi_animal"
    agency = "Chicago Animal Care and Control"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/cacc/supp_info/public_notice.html"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".page-description ul li"):
            start_str = "".join(item.xpath(".//text()").extract()).strip()
            dt_matches = [
                m[0]
                for m in re.findall(
                    r"([A-Z][a-z]{2,9},? \d\d?,? \d{4}( - \d\d?:?\d?\d?\s?[apm]{2}?))",  # noqa
                    start_str.replace(".", ""),
                )
            ]
            if not len(dt_matches) > 0:
                continue
            dt_str = dt_matches[-1]
            try:
                start_dt = dateparse(dt_str)
            except ValueError:
                continue

            meeting = Meeting(
                title="Advisory Board",
                description="",
                classification=ADVISORY_COMMITTEE,
                start=start_dt,
                end=start_dt + timedelta(hours=3),
                time_notes="Estimated 3 hour duration",
                all_day=False,
                location={
                    "name": "David R. Lee Animal Care Center",
                    "address": "2741 S. Western Ave, Chicago, IL 60608",
                },
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting, text=start_str)

            yield meeting

    def _parse_links(self, item, response):
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links
