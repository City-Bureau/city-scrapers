import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiZoningBoardSpider(CityScrapersSpider):
    name = "chi_zoning_board"
    agency = "Chicago Zoning Board of Appeals"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/dcd/supp_info/zoning_board_of_appeals.html"  # noqa
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        columns = self.parse_meetings(response)
        for column in columns:
            year = column.xpath("preceding::strong[1]/text()").re_first(r"(\d{4})(.*)")
            meetings = column.xpath("text()[normalize-space()]").extract()
            for item in meetings:
                if not item.strip():
                    continue
                start = self._parse_start(item, year)
                if start < last_year and not self.settings.getbool(
                    "CITY_SCRAPERS_ARCHIVE"
                ):
                    continue
                meeting = Meeting(
                    title="Board of Appeals",
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    time_notes="",
                    all_day=False,
                    location={
                        "name": "City Hall",
                        "address": "121 N LaSalle St Chicago, IL 60602",
                    },
                    source=response.url,
                )
                meeting["links"] = self._parse_links(column, meeting, response)
                meeting["id"] = self._get_id(meeting)
                meeting["status"] = self._get_status(meeting)
                yield meeting

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
            //td[preceding::p/strong[1]/text()[
                contains(., "Meeting Schedule")
                ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_start(item, year):
        m = re.search(r"(?P<month>\w+)\s(?P<day>\d+).*", item.strip())
        dt = datetime.strptime(
            m.group("month") + " " + m.group("day") + " " + year, "%B %d %Y"
        )
        # time based on examining meeting minutes
        return datetime.combine(dt.date(), time(9))

    @staticmethod
    def _parse_links(item, data, response):
        month = data["start"].strftime("%B")
        xp = './/a[contains(@title, "{0}")]'.format(month)
        documents = item.xpath(xp)
        if len(documents) >= 0:
            return [
                {
                    "href": response.urljoin(document.xpath("@href").extract_first()),
                    "title": document.xpath("text()").extract_first(),
                }
                for document in documents
            ]
        return []
