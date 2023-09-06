from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import scrapy
import re
import datetime as dt

class ChiNorthwestHomeEquitySpider(CityScrapersSpider):
    name = "chi_northwest_home_equity"
    agency = "Chicago Northwest Home Equity"
    timezone = "America/Chicago"
    start_urls = ["https://nwheap.com/category/meet-minutes-and-agendas/"]
     
        
    def parse(self, response, url_to_local=None):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for link in response.css('div.em-events-widget a::attr(href)').getall():
            if link != 'https://nwheap.com/events/':
                if url_to_local:
                    link = "file:\\"+url_to_local[link]
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
        yield meeting
       
        # for item in response.css(".meetings"):
        #     meeting = Meeting(
        #         title=self._parse_title(item),
        #         description=self._parse_description(item),
        #         classification=self._parse_classification(item),
        #         start=self._parse_start(item),
        #         end=self._parse_end(item),
        #         all_day=self._parse_all_day(item),
        #         time_notes=self._parse_time_notes(item),
        #         location=self._parse_location(item),
        #         links=self._parse_links(item),
        #         source=self._parse_source(response),
        #     )

            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            # yield meeting

    def _parse_title(self, item):
        return item.css("h1.entry-title::text").get()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return self._parse_date(item, start_time=True)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return self._parse_date(item, start_time=False)

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        location_ = item.css('p > strong:contains("Location") ~ a::text').get()

        return {
            "address": location_,
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _parse_date(self, item, start_time=True):
        date = item.css('p:contains("Date/Time")').get()
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', date)
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

