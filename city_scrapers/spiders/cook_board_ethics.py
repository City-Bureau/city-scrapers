from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookBoardEthicsSpider(CityScrapersSpider):
    name = "cook_board_ethics"
    agency = "Cook County Government Board of Ethics"
    timezone = "America/Chicago"
    allowed_domains = ["www.cookcountyil.gov"]

    def start_requests(self):
        today = datetime.now()
        for month_delta in range(-2, 3):
            mo_str = (today + relativedelta(months=month_delta)).strftime("%Y-%m")
            url = (
                f"https://www.cookcountyil.gov/calendar-node-field-date/month/{mo_str}"
            )
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
            classification=BOARD,
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
        Get urls for all Board of ethics meetings on the page.
        """
        return [
            response.urljoin(href)
            for href in response.xpath('//a[contains(text(), "Board of Ethics")]')
            .css("a::attr(href)")
            .extract()
        ]

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        address = response.xpath(
            '//div[@class="field event-location"]/descendant::*/text()'
        ).extract()
        for word in ["Location:", ", ", " "]:
            address.remove(word)
        address = " ".join(address)
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
        title = response.xpath("//h1/text()").extract_first()
        if "Special" in title:
            return "Special Board of Ethics Meeting"
        elif "Board of Ethics" in title:
            return "Board of Ethics"
        else:
            return title

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
