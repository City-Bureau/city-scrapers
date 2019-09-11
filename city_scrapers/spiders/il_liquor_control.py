import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlLiquorControlSpider(CityScrapersSpider):
    name = "il_liquor_control"
    agency = "Illinois Liquor Control Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www2.illinois.gov"]
    start_urls = [
        "https://www2.illinois.gov/ilcc/Divisions/Pages/Legal/"
        "Hearing-Schedule-for-Chicago-IL-and-Springfield-IL.aspx"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping

        Each tentative meeting has own page. start_url is only used to get links for the pages.
        """
        if response.url == self.start_urls[0]:
            for meeting_href in response.css('div.soi-link-item a::attr(href)').extract():
                yield response.follow(meeting_href, callback=self.parse)
        else:
            """
            Extract date time and location information from each meeting date.
            Store the info in the variables.
            The variables are passed onto '_parse_location', '_parse_start', '_parse_end'.
            """
            dt_str = ' '.join([
                x.strip() for x in response.css('div.soi-event-data::text').extract()
            ])
            loc_str = ' '.join([
                x.strip() for x in response.css('div.soi-eventlocation div::text').extract()
            ])
            meeting = Meeting(
                title=self._parse_title(response),
                description='',
                classification=BOARD,
                start=self._parse_start(dt_str),
                end=self._parse_end(dt_str),
                all_day=False,
                time_notes='',
                location=self._parse_location(loc_str),
                links={},
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return response.css('p.soi-eventType::text').extract_first().strip()

    def _parse_start(self, dt_str):
        """Parse start datetime as a naive datetime object."""

        return datetime.datetime.strptime(' '.join(dt_str.split()[:6]), '%A, %B %d, %Y %I:%M %p')

    def _parse_end(self, dt_str):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return datetime.datetime.strptime(
            ' '.join(dt_str.split()[:4] + dt_str.split()[7:]), '%A, %B %d, %Y %I:%M %p'
        )

    def _parse_location(self, loc_str):
        """Parse or generate location."""
        return {
            "address": '{} Chicago, IL'.format(' '.join(loc_str.split()[:4])),
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
