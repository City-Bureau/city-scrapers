import re

import dateutil.parser
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiBoardOfEthicsSpider(CityScrapersSpider):
    name = 'chi_boardofethics'
    agency = 'Chicago Board of Ethics'
    allowed_domains = ['chicago.gov']
    start_urls = ['https://www.chicago.gov/city/en/depts/ethics/supp_info/minutes.html']

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        root = response.xpath('//h3[text() = "Meeting Schedule"]/..')
        description = root.css('p::text').extract_first()
        description = description.strip() if description else ''
        meeting_dates = root.css('tbody tr td::text').extract()
        meeting_dates = [m for m in meeting_dates if m.strip() != '']

        location = self._parse_location(description)

        # Ethics board only displays are tables with all meeting dates
        # so the crawler only processes a single page that displays different
        # dates so most of the attributes are the same.
        for meeting_date in meeting_dates:
            start = self._parse_start(meeting_date, description)
            meeting = Meeting(
                title='Board of Directors',
                description=description,
                classification=BOARD,
                start=start,
                end=None,
                time_notes='',
                all_day=False,
                location=location,
                links=self._parse_links(start, response),
                source=response.url,
            )
            meeting['id'] = self._get_id(meeting)
            meeting['status'] = self._get_status(meeting, text=meeting_date)
            yield meeting

    @staticmethod
    def _parse_start(date_str, description):
        """Parse state datetime."""
        time_match = re.search(r'(1[0-2]|0?[1-9]):([0-5][0-9])( ?[AP]M)?', description)
        return dateutil.parser.parse('{} {}'.format(date_str, time_match.group(0)))

    @staticmethod
    def _parse_location(text):
        name = re.compile(r'(held at the) (?P<name>.*?),(?P<address>.*).')
        matches = name.search(text)
        location_name = matches.group('name').strip()
        address = matches.group('address').strip()
        return {
            'name': location_name,
            'address': address,
        }

    def _parse_links(self, start, response):
        links = []
        for link_el in response.css('.page-full-description a[title$="{}"]'.format(start.year)):
            if start.strftime('%B') in link_el.xpath('./text()').extract_first():
                links.append({
                    'title': 'Minutes',
                    'href': response.urljoin(link_el.xpath('@href').extract_first())
                })
        return links
