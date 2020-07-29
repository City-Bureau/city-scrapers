from datetime import datetime
from datetime import timedelta

from scrapy import Request

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiOhareNoise2Spider(CityScrapersSpider):
    name = "chi_ohare_noise_2"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"
    start_urls = ["https://www.oharenoise.org/meetings-all/year.listevents/2020/07/22/-"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".ev_td_li"):
            surl = self._parse_url(item)
            yield Request(url=response.urljoin(surl), callback=self._parse_subpage)

            #meeting["status"] = self._get_status(meeting)
            #meeting["id"] = self._get_id(meeting)

            #yield meeting

    def _parse_subpage(self, response):
#        stime = self._parse_start(response)
#        meeting = Meeting(
#        self._parse_title(response),
#            description=self._parse_description(response),
#            classification=self._parse_classification(response),
#            start=stime,
#            end=stime+timedelta(hours=1),
#            all_day=self._parse_all_day(response),
#            time_notes=self._parse_time_notes(response),
#            location= None,
#            links=self._parse_links(response),
#            source=self._parse_source(response),
#        )
#
#        yield meeting

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return response.xpath("//div[@class='jev_evdt_header']/div/h2/text()").extract()[0]

    def _parse_url(self, item):
        """Parse or generate meeting title."""
        return  [i.strip() for i in item.xpath('p/a/@href').extract()][0]

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(item.xpath('p/text()').extract()[1].strip(), '%A, %B %d, %Y %I:%M%p')

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
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
