import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthernIlUniversitySpider(CityScrapersSpider):
    name = "chi_northern_il_university"
    agency = "Northeastern Illinois University"
    timezone = "America/Chicago"
    start_urls = ["https://www.neiu.edu/about/board-of-trustees/board-meeting-materials"]

    def parse(self, response):
        self.link_date_map = defaultdict(list)
        link_list = response.xpath(
            '//div[@class="field field--name-field-generic-body field--type-text-long \
field--label-hidden field--item"]/h3'
        )
        for title in link_list:
            full_str = title.xpath(".//text()").extract()[0]
            date = full_str.split("-")[0].split("(")[0]

            date_obj = datetime.strptime(date.strip(" "), '%B %d, %Y')
            new_date_obj = datetime(date_obj.year, date_obj.month, date_obj.day, 13, 00)
            for one_day_links in title.xpath('.//following-sibling::ul[1]/li'):
                href = one_day_links.xpath('.//@href').get()
                name = one_day_links.xpath('.//text()').extract()
                if href is None:
                    link = ''
                else:
                    link = response.urljoin(href)
                self.link_date_map.setdefault(new_date_obj, []).append({
                    "title": ''.join(name),
                    "href": link
                })
        yield response.follow(
            "https://www.neiu.edu/about/board-of-trustees/calendar-of-meetings",
            callback=self._parse_detail
        )

    def _parse_detail(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        items_list = response.xpath(
            '//div[@class="field field--name-field-generic-body field--type-text-long \
field--label-hidden field--item"]'
        )
        year_list = items_list.xpath('.//h2')
        for years in year_list.extract():
            year = re.findall(r'\d{4}', years)[0]
            items = year_list.xpath('.//following-sibling::ul[1]/li').extract()
            for item in items:
                start = self._parse_start(item, year)
                meeting = Meeting(
                    title=self._parse_title(item),
                    description='',
                    classification=self._parse_classification(item),
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="See agenda for meeting time",
                    location=self._parse_location(item),
                    links=self.link_date_map[start],
                    source=self._parse_source(response),
                )
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_obj = item.split('-')
        title = str()
        for i in range(1, len(title_obj)):
            title = title + title_obj[i]
        title = re.sub(r'<strong>|</strong>|<li>|</li>|\xa0', ' ', title)
        return title.strip(" ")

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if 'committee' in title.lower():
            return COMMITTEE
        if "meeting" in title.lower():
            return BOARD
        return NOT_CLASSIFIED

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object."""
        date = re.sub(r'<li>|,|\xa0|\*|\*\*|<strong>|</strong>', '', item.split("-")[0]).strip(" ")
        date_obj = datetime.strptime(date, '%A %B %d')
        new_date_obj = datetime(int(year), date_obj.month, date_obj.day, 13, 00)
        return new_date_obj

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_location(self, item):
        """Parse or generate location."""
        if "**" in item:
            return {
                "address": "",
                "name": "Jacob H. Carruthers Center",
            }
        if "*" in item:
            return {"address": "", 'name': "El Centro"}
        return {
            "address": "5500 North St. Louis Avenue, Chicago, Ill., 60625",
            "name": 'Northeastern Illinois University'
        }

    def _parse_links(self):
        """Parse or generate links."""
        return ''

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
