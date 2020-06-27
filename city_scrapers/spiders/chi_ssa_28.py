import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiSsa28Spider(CityScrapersSpider):
    name = "chi_ssa_28"
    agency = "Chicago Special Service Area #28 Six Corners"
    timezone = "America/Chicago"
    start_urls = ["https://sixcorners.com/ssa28"]
    location = {
        "name": "Portage Arts Lofts",
        "address": "4041 N. Milwaukee Ave. #302, Chicago, IL 60641",
    }

    def parse(self, response):
        """
        Since the meeting dates are in an unordered text block, we'll need to parse
        them outside of the main parsing loop, and use the list index to iterate through
        xpath for things like links.
        """
        self._validate_location(response)
        block_item = response.css(".sqs-layout > div > .sqs-col-3")[:1].css(
            ".sqs-block-content"
        )[0]
        block_text = "".join(block_item.extract())
        year_match = re.search(
            r"\d{4}", " ".join(block_item.css("strong::text").extract())
        )
        if year_match:
            year_str = year_match.group()
        else:
            year_str = str(datetime.today().year)

        for block_str in re.split(r"\<br *\/?\>", block_text):
            item = Selector(text=block_str)
            start = self._parse_start(item, year_str)
            if not start:
                continue

            meeting = Meeting(
                title="Six Corners Commission",
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting, text=block_str)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _validate_location(self, response):
        if (
            "4041 N"
            not in response.xpath(
                '//div[@class="col sqs-col-3 span-3"]/div/div/p[1]/em/text()'
            ).get()
        ):
            raise ValueError("Meeting location has changed")

    def _parse_start(self, item, year_str):
        """Parse start datetime as a naive datetime object."""
        date_match = re.search(
            r"[A-Z][a-z]{2,8} \d{1,2}", " ".join(item.css("*::text").extract())
        )
        if not date_match:
            return
        return datetime.strptime(
            " ".join([date_match.group(), "1:30pm", year_str]), "%B %d %I:%M%p %Y"
        )

    def _parse_links(self, item, response):
        """Parse or generate links. Uses the index from the dates list."""
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links
