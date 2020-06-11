import re
from datetime import datetime

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiPlanCommissionSpider(CityScrapersSpider):
    name = "chi_plan_commission"
    agency = "Chicago Plan Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission.html"
    ]
    location = {"name": "City Hall", "address": "121 N LaSalle St Chicago, IL 60602"}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for meeting_group in response.css(".page-full-description table[cellspacing]"):
            year_str = meeting_group.xpath("preceding::strong[1]/text()").re_first(
                r"\d{4}"
            )
            for column in meeting_group.css("td").extract():
                for item_str in re.split(r"\<br\s*\/?\>", column):
                    item = Selector(text=item_str)
                    start = self._parse_start(item, year_str)
                    if start is None or (
                        start < last_year
                        and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                    ):
                        continue
                    links = self._parse_links(item, response)
                    detail_links = [
                        link["href"]
                        for link in links
                        if link["href"].endswith(".html")
                        and "postpone" not in link["title"].lower()
                    ]
                    if len(detail_links) > 0:
                        for link in detail_links:
                            yield response.follow(
                                link,
                                callback=self._parse_detail,
                                cb_kwargs={"start": start},
                            )
                        continue
                    meeting = Meeting(
                        title="Commission",
                        description="",
                        classification=COMMISSION,
                        start=start,
                        end=None,
                        time_notes="",
                        all_day=False,
                        location=self.location,
                        source=response.url,
                        links=links,
                    )
                    meeting["id"] = self._get_id(meeting)
                    meeting["status"] = self._get_status(meeting)
                    yield meeting

    def _parse_detail(self, response, **kwargs):
        start = self._parse_detail_start(response, kwargs["start"])
        detail_text = " ".join(response.css(".col-xs-12 > p *::text").extract())
        if "121 N" not in detail_text and "virtual" not in detail_text.lower():
            raise ValueError("Meeting location has changed")
        meeting = Meeting(
            title="Commission",
            description="",
            classification=COMMISSION,
            start=start,
            end=None,
            time_notes="",
            all_day=False,
            location=self.location,
            source=response.url,
            links=self._parse_detail_links(response),
        )
        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)
        yield meeting

    @staticmethod
    def _parse_start(item, year):
        item_text = " ".join(item.css("*::text").extract())
        date_match = re.search(r"[A-Z][a-z]{2,8}\.?\s+\d{1,2}", item_text)
        if not date_match:
            return
        return dateutil.parser.parse(" ".join([date_match.group(), year, "10:00am"]))

    def _parse_links(self, item, response):
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links

    def _parse_detail_start(self, response, start):
        detail_text = " ".join(response.css(".col-xs-12 > p *::text").extract())
        time_strs = re.findall(
            r"(\d{1,2}(\:\d{2})?\s+[apm\.]{2,4})", detail_text, flags=re.I
        )
        time_objs = []
        for time_str in time_strs:
            time_str = re.sub(r"[\s\.]", "", time_str[0])
            time_fmt = "%I%p"
            if ":" in time_str:
                time_fmt = "%I:%M%p"
            time_objs.append(datetime.strptime(time_str, time_fmt).time())
        if len(time_objs) > 0:
            return datetime.combine(start.date(), time_objs[0])
        return start

    def _parse_detail_links(self, response):
        links = []
        for link in response.css(".page-full-description-above a"):
            title_str = re.sub(
                r"\s+", " ", " ".join(link.css("*::text").extract())
            ).strip()
            if (
                "mailto" in link.attrib["href"]
                or link.attrib["href"].endswith("/chicago_plan_commission.html")
                or not title_str
            ):
                continue

            links.append(
                {"title": title_str, "href": response.urljoin(link.attrib["href"])}
            )
        return links
