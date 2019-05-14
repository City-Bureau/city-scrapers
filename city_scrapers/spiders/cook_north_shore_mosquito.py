import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookNorthShoreMosquitoSpider(CityScrapersSpider):
    name = "cook_north_shore_mosquito"
    agency = "Cook County North Shore Mosquito Abatement District"
    timezone = "America/Chicago"
    allowed_domains = ["www.nsmad.com"]
    start_urls = ["https://www.nsmad.com/news-events/board-meetings/"]
    TAG_RE = re.compile(r'<[^>]+>')
    location = {
        "address": "117 Northfield Road, Northfield, IL 60093",
        "name": "NSMAD Office",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._parse_location(response)
        calendar = response.xpath('//*[@id="post-68"]/div/ul/li/ul')
        for index, item in enumerate(calendar.extract()[0].split('<li>')[1:]):
            meeting = Meeting(
                title=self._parse_title(),
                description='',
                classification=self._parse_classification(),
                start=self._parse_start(response, index),
                all_day=False,
                location=self.location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting, item)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self):
        """Parse or generate meeting title."""
        return "Board of Trustees"

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, response, index):
        """Parse start datetime as a naive datetime object."""
        calendar_title = response.xpath('//*[@id="post-68"]/div/h2[1]/text()').extract()[0]
        year = ''.join([num for num in calendar_title if num.isdigit()])
        m_day = response.xpath('//*[@id="post-68"]/div/ul/li/ul/li[' + str(index + 1) + ']/text()')
        m_day = m_day.extract()[0].split('–')[0].strip()
        date = m_day + ' ' + year + ' ' + '7 pm'
        return datetime.strptime(date, '%B %d %Y %I %p')

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_location(self, response):
        """Parse or generate location."""
        if "117 North" not in response.xpath('//*[@id="post-68"]/div/p[1]/text()').extract()[0]:
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        after_dash = item.split('–')
        if len(after_dash) > 1:
            raw_link = after_dash[1].split()
            if len(raw_link) > 1 and 'a' in raw_link[0]:
                title = "Minutes" if "Minutes" in str(raw_link) else "Agenda"
                minutes_link = re.search(r'\"(.+?)\"', raw_link[1]).group(1)
                minutes = {"href": minutes_link, "title": title}
                links.append(minutes)
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
