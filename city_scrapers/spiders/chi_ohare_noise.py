from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiOhareNoiseSpider(CityScrapersSpider):
    name = "chi_ohare_noise"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"
    start_urls = ["https://www.oharenoise.org/about-oncc/agendas-and-minutes"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("tr.cat-list-row0") + response.css("tr.cat-list-row1"):
            meeting = Meeting(
                title=self._parse_title(item),
                start=self._parse_start(item),
                links=self._parse_links(item, response),
                source=self._parse_source(response),
            )

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css(".djc_category span").xpath("text()").extract()

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(item.css(".djc_producer span").xpath("text()").extract()[0], '%B %d, %Y')

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = item.xpath('td[@class="djc_price"]/div/ul/li/a')
        return [{"href": response.url+'?'+link.xpath("@href").extract()[0].split('?')[1], 
                "title": link.xpath("span/text()").extract()[0]} 
                for link in links]


    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
