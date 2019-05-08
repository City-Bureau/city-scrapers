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

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        calendar = response.xpath('//*[@id="post-68"]/div/ul/li/ul')
        for item in calendar.extract()[0].split('<li>')[1:]:
            meeting = Meeting(
                title=self._parse_title(),
                description='',
                classification=self._parse_classification(),
                start=self._parse_start(item, response),
                all_day=False,
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self):
        """Parse or generate meeting title."""
        return "Board of Trustees"

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item, response):
        """Parse start datetime as a naive datetime object."""
        year = '2019'
        calendar_title = response.xpath('//*[@id="post-68"]/div/h2[1]').extract()[0]
        if '2019' not in calendar_title:
            raise ValueError("Year no longer {}".format(year))
        month_day = self._clean_html_tags(item.split('–')[0])
        date = month_day + ' ' + year + ' ' + '7 pm'
        return datetime.strptime(date, '%B %d %Y %I %p')

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        date = item.split('–')
        if len(date) > 1:
            date = date[1]
            if 'View' not in date:
                return self._clean_html_tags(date)
        return ""

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "117 Northfield Road, Northfield",
            "name": "NSMAD Office",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        after_dash = item.split('–')
        if len(after_dash) > 1:
            raw_link = after_dash[1].split()
            if len(raw_link) > 1 and 'a' in raw_link[0]:
                minutes_link = re.search(r'\"(.+?)\"', raw_link[1]).group(1)
                minutes = {"href": minutes_link, "title": "Minutes"}
                links.append(minutes)
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _clean_html_tags(self, item):
        return self.TAG_RE.sub('', item).strip()
