from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlSportsFacilitiesAuthoritySpider(CityScrapersSpider):
    name = "il_sports_facilities_authority"
    agency = "Illinois Sports Facilities Authority"
    timezone = "America/Chicago"
    allowed_domains = ["www.isfauthority.com"]
    start_urls = ["https://www.isfauthority.com/governance/board-meetings/"]
    location = {
        'name': 'Authority offices',
        'address': 'Guaranteed Rate Field, 333 West 35th Street, Chicago, IL'
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        location = self._validate_location(response)
        for item in response.css('div .wpb_wrapper p'):
            meeting = Meeting(
                title=self._parse_title(item),
                description='',
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes='',
                location=location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            # meeting['status'] = self._get_status(meeting)
            # meeting['id'] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css('.inner-text h2::text') or item.css('p::text').re(r'.*[a-zA-Z] Meeting')

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _validate_location(self, response):
        """Parse the location of the meeting."""
        if 'Guaranteed Rate Field' not in ' '.join(
                response.css('div .wpb_wrapper .inner-test hs::text')
        ):
            return response.css(
                'div .wpb_wrapper .inner-test h2::text'
            ).re(r'\b \d* [a-zA-Z].*, [0-9][a-zA-Z].*')
        else:
            return self.location

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return item.css('::text').re(r'[0-9]*[.][0-9]*[.][0-9]*')

    def _parse_links(self, item):
        """Parse or generate links."""
        return [
            {
                "href": parsed.xpath('@href').get(),
                "title": parsed.css('::text').getall()
            } for parsed in item.css('p a')
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
