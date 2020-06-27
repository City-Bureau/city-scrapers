import re
from datetime import datetime, timedelta

import scrapy
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookCountySpider(CityScrapersSpider):
    name = "cook_county"
    agency = "Cook County Government"
    timezone = "America/Chicago"

    def start_requests(self):
        # Only filter for Public Forums (20) in the current and upcoming month
        today = datetime.now()
        next_month = today.replace(day=28) + timedelta(days=5)
        for dt in [today, next_month]:
            mo_str = dt.strftime("%Y-%m")
            url = (
                "https://www.cookcountyil.gov/calendar-node-field-date/month/{}?"
                "field_categories_tid_entityreference_filter[]=20"
            ).format(mo_str)
            yield scrapy.Request(url=url, method="GET", callback=self.parse)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

    def _parse_event(self, response):
        """Parse the event page."""
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(response),
            classification=self._parse_classification(title),
            start=self._parse_start(response),
            end=self._parse_end(response),
            time_notes="",
            all_day=self._parse_all_day(response),
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)
        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all events on the page.
        """
        return [
            response.urljoin(href)
            for href in response.css(
                ".view-item-event_calendar a::attr(href)"
            ).extract()
        ]

    @staticmethod
    def _parse_classification(name):
        name = name.upper()
        if re.search(r"A(C|(DVISORY)) (COMMITTEE|COUNCIL)", name):
            return ADVISORY_COMMITTEE
        if "BOARD" in name:
            return BOARD
        if "COMMITTEE" in name:
            return COMMITTEE
        if "COMMISSION" in name:
            return COMMISSION
        return NOT_CLASSIFIED

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        address = response.xpath(
            '//div[@class="field event-location"]/descendant::*/text()'
        ).extract()
        address = " ".join([x.strip() for x in address])
        address = address.replace("Location:", "").strip()
        return {
            "address": address,
            "name": "",
        }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        date = "".join(date).upper()
        return "ALL DAY" in date

    def _parse_title(self, response):
        """Parse or generate event title."""
        return response.xpath("//h1/text()").extract_first()

    def _parse_description(self, response):
        """
        Parse or generate event description.
        """
        category_field = response.xpath(
            "//div[contains(., 'Category:') and contains(@class, 'field-label')]"
        )
        field_items = category_field.xpath(
            "./following::div[contains(@class, 'field-items')]"
        )
        return " ".join(
            field_items.xpath(".//p/text()").extract()
            + field_items.xpath(".//strong/text()").extract()
        ).strip()

    def _parse_start(self, response):
        """
        Parse start date and time.
        """
        start = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        start = "".join(start).upper()
        start = start.split(" TO ")[0].strip()
        start = start.replace("(ALL DAY)", "12:00AM")

        return datetime.strptime(start, "%B %d, %Y %I:%M%p")

    def _parse_end(self, response):
        """
        Parse end date and time.
        """
        date = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        date = "".join(date).upper()
        date.replace("(ALL DAY)", "TO 11:59PM")
        start_end = date.split(" TO ")

        if len(start_end) < 2:
            return

        end_time = start_end[1]
        date = start_end[0][: start_end[0].rindex(" ")]
        return datetime.strptime("{} {}".format(date, end_time), "%B %d, %Y %I:%M%p")

    def _parse_links(self, response):
        files = response.css("span.file a")
        return [
            {
                "href": f.xpath("./@href").extract_first(),
                "title": f.xpath("./text()").extract_first(),
            }
            for f in files
        ]
