from datetime import datetime

from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookHousingSpider(CityScrapersSpider):
    name = "cook_housing"
    agency = "Cook County Housing Authority"
    timezone = "America/Chicago"
    allowed_domains = ["thehacc.org"]

    @property
    def start_urls(self):
        """Pull events from the calendar pages for 2 months past through 2 months ahead"""
        now = datetime.now()
        urls = []
        for months_delta in range(-2, 3):
            month_str = (now + relativedelta(months=months_delta)).strftime("%Y-%m")
            urls.append("http://thehacc.org/events/{}".format(month_str))
        return urls

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        for item in response.xpath('//div[@class="item-wrapper"]'):
            classification = self._parse_classification(item)
            if classification == BOARD:
                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=BOARD,
                    start=self._parse_times(item)[0],
                    end=self._parse_times(item)[1],
                    all_day=False,
                    time_notes="",
                    location=self._parse_location(item),
                    links=[],
                    source=self._parse_source(item),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    @staticmethod
    def _parse_title(item):
        """Parse or generate meeting title."""
        title = item.xpath(".//a/text()[normalize-space(.)]").get().strip()
        if title == "Housing Authority of Cook County Board Meeting":
            return "Board of Commissioners"
        return title

    @staticmethod
    def _parse_classification(item):
        """Parse or generate classification from allowed options."""
        title = item.xpath(".//a/text()[normalize-space(.)]").get().lower()
        if 'board' in title:
            return BOARD
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_times(item):
        """Parse start and end datetimes as a naive datetime object."""
        month = item.xpath('.//span[@class="month"]/text()').get().strip()
        day = item.xpath('.//span[@class="day"]/text()').get().strip()
        year = item.xpath('//div[@class="header"]/span[@class="month"]/text()').get().split()[1]
        ddate = datetime.strptime("%s %s %s" % (month, day, year), "%b %d %Y").date()

        times = item.xpath('.//p[@class="subtitle"]/br/following-sibling::text()').get().strip()
        ttimes = [datetime.strptime(item, "%I:%M %p") for item in times.split(" - ")]

        return datetime.combine(ddate, ttimes[0].time()), datetime.combine(ddate, ttimes[1].time())

    @staticmethod
    def _parse_location(item):
        """Parse or generate location."""
        times = item.xpath('.//p[@class="subtitle"]/br/following-sibling::text()').get().strip()
        address = item.xpath('.//div[@class="info"]/p/text()').get().replace(times, '').strip()
        name = item.xpath('.//p[@class="subtitle"]/text()').get().strip()
        return {"address": address + ", Chicago, IL", "name": name}

    @staticmethod
    def _parse_source(item):
        """Parse or generate source."""
        return item.xpath('.//div[@class="info"]//a/@href').get()
