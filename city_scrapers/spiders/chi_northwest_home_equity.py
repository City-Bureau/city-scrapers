import datetime as dt
import re

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthwestHomeEquitySpider(CityScrapersSpider):
    name = "chi_northwest_home_equity"
    agency = "Chicago Northwest Home Equity"
    timezone = "America/Chicago"
    start_urls = ["https://nwheap.com/category/meet-minutes-and-agendas/"]

    def parse(self, response):
        for link in response.css("div.em-events-widget a::attr(href)").getall():
            if link != "https://nwheap.com/events/":
                yield scrapy.Request(link, callback=self.parse_page)

    def parse_page(self, response):
        meeting = Meeting(
            title=self._parse_title(response),
            description=self._parse_description(response),
            classification=self._parse_classification(response),
            start=self._parse_start(response),
            end=self._parse_end(response),
            all_day=self._parse_all_day(response),
            time_notes=self._parse_time_notes(response),
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=self._parse_source(response),
        )
        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)
        return meeting

    def _parse_title(self, item):
        return item.css("h1.entry-title::text").get()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        return COMMISSION

    def _parse_start(self, item):
        return self._parse_date(item, start_time=True)

    def _parse_end(self, item):
        return self._parse_date(item, start_time=False)

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        location_ = item.css('p > strong:contains("Location") ~ a::text').get()

        return {
            "address": location_,
            "name": "",
        }

    def _parse_links(self, item):
        loc_link = item.css('p > strong:contains("Location") ~ a::attr(href)').get()
        title = item.css('p > strong:contains("Location") ~ a::text').get()
        return [{"href": loc_link, "title": title}]

    def _parse_source(self, response):
        return response.url

    def _parse_date(self, item, start_time=True):
        date = item.css('p:contains("Date/Time")').get()
        date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", date)
        date = date_match.group(0)

        time = item.css('p > strong:contains("Date/Time") ~ *::text').get()
        start, end = "", ""
        if not time:
            start = "Not found"
            end = "Not found"
        else:
            start, end = time.split(" - ")
        if start_time:
            return dt.datetime.strptime(f"{date} {start}", "%m/%d/%Y %I:%M %p")
        return dt.datetime.strptime(f"{date} {end}", "%m/%d/%Y %I:%M %p")
