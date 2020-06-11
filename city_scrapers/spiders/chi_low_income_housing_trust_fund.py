import re
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLowIncomeHousingTrustFundSpider(CityScrapersSpider):
    name = "chi_low_income_housing_trust_fund"
    agency = "Chicago Low-Income Housing Trust Fund"
    timezone = "America/Chicago"
    start_urls = ["http://www.clihtf.org/about-us/upcomingevents/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        items = self._parse_calendar(response)
        for item in items:
            # Drop empty links
            if "http" not in item["source"]:
                continue

            req = scrapy.Request(
                item["source"], callback=self._parse_detail, dont_filter=True,
            )
            req.meta["item"] = item
            yield req

        # Only go to the next page once, so if query parameters are set, exit
        if "?month" not in response.url:
            yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = response.css(".calendar-next a::attr(href)").extract_first()
        return scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def _parse_calendar(self, response):
        """Parse items on the main calendar page"""
        items = []
        for item in response.css(
            ".day-with-date:not(.no-events), .current-day:not(.no-events)"
        ):
            title = self._parse_title(item)
            if "training" in title.lower():
                continue
            description = self._parse_description(item)
            items.append(
                Meeting(
                    title=title,
                    description=description,
                    classification=self._parse_classification(title),
                    all_day=False,
                    links=[],
                    time_notes="",
                    source=self._parse_source(item, response.url),
                )
            )
        return items

    def _parse_detail(self, response):
        """Parse detail page for additional information"""
        meeting = response.meta.get("item", {})
        meeting.update(self._parse_start_end_time(response))
        meeting["location"] = self._parse_location(response)
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        return meeting

    def _parse_title(self, item):
        """Parse or generate event title"""
        return item.css(".event-title::text").extract_first()

    def _parse_description(self, item):
        """Parse or generate event description"""
        return (
            item.xpath(
                './/span[@class="event-content-break"]/following-sibling::text()'
            ).extract_first()
            or ""
        )

    def _parse_classification(self, title):
        """Parse or generate classification (e.g. board, committee, etc)"""
        if "board" in title.lower():
            return BOARD
        if "committe" in title.lower():
            return COMMITTEE
        return NOT_CLASSIFIED

    def _parse_start_end_time(self, response):
        """Parse start and end datetimes"""
        time_str = response.css(".cc-panel .cc-block > span::text").extract_first()
        time_str = re.sub(r"\s+", " ", time_str)
        date_str = re.search(r"(?<=day, ).*(?= fro)", time_str).group().strip()
        start_str = re.search(r"(?<=from ).*(?= to)", time_str).group().strip()
        end_str = re.search(r"(?<=to ).*(?= \w{3})", time_str).group().strip()
        date_obj = datetime.strptime(date_str, "%B %d, %Y").date()
        start_time = datetime.strptime(start_str, "%I:%M %p").time()
        end_time = datetime.strptime(end_str, "%I:%M %p").time()
        return {
            "start": datetime.combine(date_obj, start_time),
            "end": datetime.combine(date_obj, end_time),
        }

    def _parse_location(self, response):
        """Parse or generate location"""
        addr_sel = response.css(
            ".cc-panel .cc-block:nth-child(2) > span:nth-of-type(2)::text"
        )
        if not addr_sel:
            addr_sel = response.css("#span_event_where_multiline p:first-of-type::text")
        addr_lines = addr_sel.extract()
        return {
            "address": " ".join(
                [re.sub(r"\s+", " ", line).strip() for line in addr_lines]
            ),
            "name": "",
        }

    def _parse_source(self, item, response_url):
        """Parse or generate source"""
        item_link = item.css(".calnk > a::attr(href)").extract_first()
        if item_link:
            return item_link
        return response_url
