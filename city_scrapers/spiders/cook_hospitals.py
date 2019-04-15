from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class CookHospitalsSpider(CityScrapersSpider):
    name = 'cook_hospitals'
    agency = 'Cook County Health and Hospitals System'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cookcountyhhs.org']
    start_urls = ['http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/']
    domain_root = 'http://www.cookcountyhhs.org'

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath("//a[@class='h2 accordion-toggle collapsed']"):
            title = self._parse_title(item)
            aria_control = item.xpath("@aria-controls").extract_first()
            item_uncollapsed = item.xpath(
                "//div[@id='{}']//tbody//td[@data-title='Meeting Information']".
                format(aria_control)
            )
            for subitem in item_uncollapsed:
                start, end = self._parse_times(subitem)
                meeting = Meeting(
                    title=title,
                    description='',
                    classification=self._parse_classification(title),
                    start=start,
                    end=end,
                    time_notes='',
                    all_day=False,
                    location=self._parse_location(subitem),
                    links=self._parse_links(subitem),
                    source=response.url,
                )
                meeting['status'] = self._get_status(meeting)
                meeting['id'] = self._get_id(meeting)
                yield meeting

    @staticmethod
    def _parse_classification(name):
        if 'BOARD' in name.upper():
            return BOARD
        return COMMITTEE

    @staticmethod
    def _parse_links(subitem):
        anchors = subitem.xpath("following-sibling::td//a")
        documents = []
        if anchors:
            for a in anchors:
                documents.append({
                    'href': a.xpath('@href').extract_first(default=''),
                    'title': a.xpath('text()').extract_first(default=''),
                })
        return documents

    @staticmethod
    def _parse_location(subitem):
        """
        Parse location
        """
        address = subitem.xpath('text()').extract()[1]
        return {
            'address': address.strip(),
            'name': '',
        }

    @staticmethod
    def _parse_title(item):
        """Get meeting title from item's text"""
        return item.xpath('text()').extract_first().strip()

    @staticmethod
    def _parse_times(subitem):
        """
        Combine start time with year, month, and day.
        """
        tokens = subitem.xpath('text()').extract_first().strip().split(' - ')
        date_obj = parse(tokens[0])
        time_obj = parse(tokens[1])
        start = datetime.combine(date_obj, time_obj.time())
        end = None
        if len(tokens) > 2:
            end = datetime.combine(date_obj, parse(tokens[2]).time())
        return start, end
