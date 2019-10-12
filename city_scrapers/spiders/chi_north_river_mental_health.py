from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthRiverMentalHealthSpider(CityScrapersSpider):
    name = "chi_north_river_mental_health"
    agency = "North River Expanded Mental Health Services Program and Governing Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.northriverexpandedmentalhealthservicescommission.org"]
    start_urls = ["http://www.northriverexpandedmentalhealthservicescommission.org/index.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".meetings"):
            meeting = Meeting(
                title="Governing Commission",
                description='',
                classification="COMMISSION",
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes='',
                location={
                    "name": "North River Expanded Mental Health Services Program Governing Commission Office",
                    "address": "3525 W. Peterson Ave, Unit 306, Chicago, IL 60659",
                },
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.xpath("//div[@class=‘paragraph’][2]/font[1]/font[2]/text()[1]").get()
        time = item.xpath("//div[@class=‘paragraph’][2]/font[1]/font[2]/text()[2]").get()
        date_time = date + ‘ ‘ + time
        return datetime.strptime(date_time,"%A: %B %d, %Y @ %I %p")

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        document = item.xpath(“//a[@href=‘/minutes.html’]”).get()
        for link in document:
            links.append({
            “href”: response.urljoin(link.xpath(‘@href’)).get(),
            “title”: “Minutes”,
            })
        return links
