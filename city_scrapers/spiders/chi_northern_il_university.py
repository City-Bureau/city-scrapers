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
        for title in response.css(".field--name-field-generic-body h3"):
            full_str = title.xpath(".//text()").extract()[0]
            date_match = re.search(r"[a-z]{3,9} \d{1,2},? \d{4}", full_str, flags=re.I)[0]
            date_obj = datetime.strptime(re.sub(',', '', date_match), '%B %d %Y')
            new_date_obj = datetime(date_obj.year, date_obj.month, date_obj.day, 13, 00)
            for one_day_links in title.xpath('.//following-sibling::ul[1]/li'):
                href = one_day_links.xpath('.//@href').get()
                name = one_day_links.xpath('.//text()').extract()
                if href is None:
                    continue
                else:
                    link = response.urljoin(href)
                self.link_date_map.setdefault(new_date_obj, []).append({
                    "title": "".join(name),
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
        for years in year_list:
            year = re.search(r'\d{4}', years.extract()).group(0)
            for items in years.xpath('.//following-sibling::ul[1]/li'):
                item = items.extract()
                start = self._parse_start(items, year)
                meeting = Meeting(
                    title=self._parse_title(items),
                    description='',
                    classification=self._parse_classification(item),
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="See agenda for meeting time",
                    location=self._parse_location(item),
                    links=self.link_date_map.get(start, []),
                    source=response.url,
                )
                if "Rescheduled" in meeting["title"]:
                    meeting["status"] = "Rescheduled"
                    meeting["title"] = re.sub(r"Rescheduled", "", meeting["title"]).strip()
                else:
                    meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_obj = item.xpath(".//text()").extract()
        title = re.sub(r'\(.+\)', '', "".join(title_obj))
        title = title.split("-")[-1].strip(" ")
        return title

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if 'committee' in title.lower():
            return COMMITTEE
        if "meeting" in title.lower():
            return BOARD
        return NOT_CLASSIFIED

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object."""
        item = item.xpath(".//text()").extract()[0].split("-")[0].strip()
        date = re.sub(r',|\xa0|\*|\*\*', '', item).strip(" ")
        date_obj = datetime.strptime(date, '%A %B %d')
        new_date_obj = datetime(int(year), date_obj.month, date_obj.day, 13, 00)
        return new_date_obj

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
