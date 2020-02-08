from datetime import datetime
import sys 

from city_scrapers_core.constants import PASSED, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider



def print_node(node):
    print(node.xpath('string(.)').get())



class ChiSouthwestHomeEquityISpider(CityScrapersSpider):
    name = "chi_southwest_home_equity_i"
    agency = "Chicago Southwest Home Equity Commission I"
    timezone = "America/Chicago"
    allowed_domains = ["swhomeequity.com"]
    start_urls = ["https://swhomeequity.com/agenda-%26-minutes"]
    location = {
        "name": "Southwest Home Equity Assurance office",
        "address": "5334 W. 65th Street in Chicago, Illinois"
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        # Need to filter
        table = response.xpath('body/div/div/div/div[2]/div[3]/div/div/section/div/div[2]')

        for agenda_node in table.xpath('div[@data-ux="GridCell"][contains(., \'Agenda\')]'):
            minutes_node = agenda_node.xpath('following-sibling::div[@data-ux="GridCell"][contains(., \'Minutes\')]')
            
            agenda_contents = None
            minutes_contents = None

            meeting = Meeting(
                title=self._parse_title(agenda_contents),
                description='',
                classification=COMMISSION,
                start=self._parse_start(agenda_contents),
                end=None,
                all_day=False,
                time_notes=self._parse_time_notes(minutes_contents),
                location=self.location,
                links=self._parse_links([agenda_node, minutes_node]),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""

        return ""


    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime(2019, 4, 8, 6, 30)

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_links(self, nodes):
        links = []
        for node in nodes:
            if node:
                links.append({
                        "title": self._get_name(node),
                        "href": self._get_link(node)
                    })
        return links

    def _get_name(self, node):
        name = node.xpath('string(.)').get()
        return name.replace('Download','')

    def _get_link(self, node):
        return node.xpath('a/@href').get()
    
    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url


