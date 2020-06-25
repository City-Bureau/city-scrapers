import scrapy
from datetime import datetime
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class ChiSsa4Spider(CityScrapersSpider):
    name = "chi_ssa_4"
    agency = "Chicago Special Service Area #4 South Western Avenue"
    timezone = "America/Chicago"
    # start_urls = ["https://95thstreetba.org/events/category/board-meeting/"]

    def start_requests(self):
        today = datetime.now()
        for month_delta in range(-2, 3):
            mo_str = (today + relativedelta(months=month_delta)).strftime("%Y-%m")
            url = 'https://95thstreetba.org/events/category/board-meeting/month/?{}'.format(mo_str)
            yield scrapy.Request(url=url, method='GET', callback=self.parse)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

    def _parse_event(self, response):
        '''Parse the event page'''
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

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all meetings on the calendar page
        """
        return [
            href
            for href in response.css('table h3 a::attr(href)').getall()
        ]

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return "".join(response.css('div.tribe-events-single h1::text').get())

    def _parse_description(self, response):
        """Parse or generate meeting description."""
        return "".join(response.css('div.tribe-events-single-event-description p::text').getall())

    def _parse_classification(self, response):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, response):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, response):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, response):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, response):
        """Parse or generate location."""
        name = response.css('dd.tribe-venue::text').get()
        event_address = response.css('span.tribe-address')
        street = event_address.css('span.tribe-street-address::text').get()
        locality = event_address.css('span.tribe-locality::text').get() + ","
        region = event_address.css('span.tribe-region::text').get()
        postal_code = event_address.css('span.tribe-postal-code::text').get()
        country = event_address.css('span.tribe-country-name::text').get()
        # address = response.css('span.tribe-address *::text').getall()
        address = " ".join([street, locality, region, postal_code, country])

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, response):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
