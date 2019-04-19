from datetime import datetime
import re

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiInfrastructureTrustSpider(CityScrapersSpider):
    name = "chi_infrastructure_trust"
    agency = "Chicago Infrastructure Trust"
    timezone = "America/Chicago"
    allowed_domains = ["chicagoinfrastructure.org"]
    start_urls = ["http://chicagoinfrastructure.org/public-records/meeting-records-2/",
        "http://chicagoinfrastructure.org/public-records/scheduled-meetings/"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        if response.url == self.start_urls[0]:
            for item in response.css(".entry").xpath('.//p'):
                if item.xpath('.//span'):
                    continue

                yield self._generate_meeting(item, response)
        
        elif response.url == self.start_urls[1]:
            item = response.css(".entry").xpath('.//p')[1]

            yield self._generate_meeting(item, response)
    
    def _generate_meeting(self, item, response):
        """Generate the meeting object"""
        meeting = Meeting(
            title=self._parse_title(item),
            description=self._parse_description(item),
            classification=self._parse_classification(item),
            start=self._parse_start(item, response),
            end=self._parse_end(item),
            all_day=self._parse_all_day(item),
            time_notes=self._parse_time_notes(item),
            location=self._parse_location(item),
            links=self._parse_links(item),
            source=self._parse_source(response),
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        return meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Board Meeting"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item, response):
        """Parse start datetime as a naive datetime object."""
        item_html = item.get()
        date_arr = re.split('strong>| – |<|p>', item_html)
        date_arr_clean = [x for x in date_arr if x]
        date_str = date_arr_clean[0].replace(" ", "").replace("\xa0", "").strip('stndrdth')
        if response.url == self.start_urls[0]:
            return datetime.strptime(date_str, '%B%d,%Y')
        elif response.url == self.start_urls[1]:
            return datetime.strptime(date_str + str(datetime.now().year), '%A,%B%d%Y')

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "140 South Dearborn Street, Suite 1400, Chicago, IL 60603",
            "name": "Metropolitan Planning Council",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []

        item_links = item.xpath('./following-sibling::ul[1]')

        for link in item_links.xpath('.//li'):
            links.append({
                "href": link.xpath('.//a/@href').get(),
                "title": link.xpath('.//a/text()').get(),
            })
        return links if links else [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
