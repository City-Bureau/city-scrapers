from datetime import datetime

from city_scrapers_core.constants import BOARD, FORUM, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookHousingSpider(CityScrapersSpider):
    name = "cook_housing"
    agency = "Cook County Housing Authority"
    timezone = "America/Chicago"
    allowed_domains = ["thehacc.org"]
    start_urls = ["http://thehacc.org/events/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath('//div[@class="item-wrapper"]'):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_times(item)[0],
                end=self._parse_times(item)[1],
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    @staticmethod
    def _parse_title(item):
        """Parse or generate meeting title."""
        return item.xpath(".//a/text()[normalize-space(.)]").get().strip()

    @staticmethod
    def _parse_description(item):
        """Parse or generate meeting description."""
        return item.xpath('.//p[@class="subtitle"]/following-sibling::p[2]/text()').get().strip()

    @staticmethod
    def _parse_classification(item):
        """Parse or generate classification from allowed options."""
        title = item.xpath(".//a/text()[normalize-space(.)]").get().lower()
        if 'board' in title:
            return BOARD
        elif 'workshop' in title:
            return FORUM
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
        return {"address": address, "name": name}

    @staticmethod
    def _parse_links(item):
        """Parse or generate links."""
        link = item.xpath('.//div[@class="info"]//a')
        return [{"href": link.xpath('@href').get(), "title": link.xpath('text()').get()}]

    @staticmethod
    def _parse_source(response):
        """Parse or generate source."""
        return response.url
