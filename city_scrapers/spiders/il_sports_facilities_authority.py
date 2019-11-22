from datetime import datetime, timedelta

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
        for item in response.css('div.wpb_text_column div.wpb_wrapper div.inner-text h2'):
            meeting = Meeting(
                title=self._parse_h2_title(item),
                description='',
                classification=BOARD,
                start=self._parse_h2_start(item),
                end=None,
                all_day=False,
                time_notes='',
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )
            try:
                meeting['status'] = self._get_status(meeting)
                meeting['id'] = self._get_id(meeting)
            except TypeError:
                continue
            yield meeting

        for item in response.css('div.wpb_text_column div.wpb_wrapper p'):
            meeting = Meeting(
                title=self._parse_title(item),
                description='',
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes='',
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )
            try:
                meeting['status'] = self._get_status(meeting)
                meeting['id'] = self._get_id(meeting)
            except TypeError:
                continue
            yield meeting

    def _parse_title(self, item):
        """Parse meeting title."""
        return item.css('::text').re_first(r'.*[a-zA-Z] Meeting')

    def _parse_h2_title(self, item):
        """Parse meeting title from the h2 tag."""
        return item.css('::text').re_first(r'.*[a-zA-Z] Meeting').replace('Next ', '')

    def _parse_location(self, item):
        """Parse the location of the meeting."""
        return {
            'name': '',
            'address': item.css('::text').re_first(r'\b \d* [a-zA-Z].*, [0-9][a-zA-Z].*').lstrip(' ')
        }

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        parsed = item.css('::text').re_first(r'[0-9]*[.][0-9]*[.][0-9]*')
        if parsed:
            try:
                val = datetime.strptime(parsed, '%m.%d.%Y') + timedelta(hours=10)
            except ValueError:
                val = datetime.strptime(parsed, '%m.%d.%y') + timedelta(hours=10)
            return val

    def _parse_h2_start(self, item):
        """Parse start datetime from h2 tag."""
        parsed = item.css('::text').re_first(
            r'[a-zA-Z]* [0-9]*, [0-9]* at [0-9]*[:][0-9]* [APM.]*'
        ).replace('.', '')
        return datetime.strptime(parsed, '%B %d, %Y at %I:%M %p')


    def _parse_links(self, item):
        """Parse or generate links."""
        return [{
            "href": parsed.xpath('@href').get(),
            "title": parsed.css('::text').get()
        } for parsed in item.css('a')]
