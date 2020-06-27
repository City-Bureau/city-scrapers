import re
from datetime import datetime

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiDevelopmentFundSpider(CityScrapersSpider):
    name = "chi_development_fund"
    agency = "Chicago Development Fund"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_developmentfund.html"  # noqa
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        columns = self.parse_meetings(response)
        last_year = datetime.today().replace(year=datetime.today().year - 1)
        for column in columns:
            meeting_date_xpath = """text()[normalize-space()]|
                                    p/text()[normalize-space()]|
                                    ul//text()[normalize-space()]"""
            meetings = column.xpath(meeting_date_xpath).extract()
            meetings = self.format_meetings(meetings)
            for item in meetings:
                start = self._parse_start(item)
                if start is None or (
                    start < last_year
                    and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                ):
                    continue
                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    time_notes="See agenda for time",
                    all_day=False,
                    location={
                        "name": "City Hall",
                        "address": "121 N LaSalle St, Room 1000, Chicago, IL 60602",
                    },
                    source=response.url,
                    links=self._parse_links(column, item, response),
                )
                meeting["id"] = self._get_id(meeting)
                meeting["status"] = self._get_status(meeting)
                yield meeting

    @staticmethod
    def format_meetings(meetings):
        # translate and filter out non-printable spaces
        meetings = [meeting.replace("\xa0", " ").strip() for meeting in meetings]
        meetings = list(filter(None, meetings))
        return meetings

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
                //td[preceding::strong[1]/text()[
                    contains(., "Meetings")
                    ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_title(meeting):
        if "advisory" in meeting.lower():
            return "Advisory Board"
        return "Board of Directors"

    @staticmethod
    def _parse_start(meeting):
        # Not all dates on site a valid dates (e.g. Jan. 2011), so try to parse
        # and return none if not possible
        clean_str = re.sub(r"[\.,]", "", meeting)
        date_str = re.search(r"[a-zA-z]{1,10} \d{1,2} \d{4}", clean_str)
        if not date_str:
            return
        return dateutil.parser.parse(date_str.group())

    def _parse_links(self, item, meeting, response):
        """
        Find <a> tags where 1st, non-blank, preceding text = meeting (e.g. 'Jan 16')
        site is pretty irregular and text is sometimes nested, so check siblings
        children for meeting name if not found for sibling
        """
        anchor_xpath = """
            //a[preceding-sibling::text()[normalize-space()][1][contains(., "{}")]]
        """.format(
            meeting
        )
        documents = item.xpath(anchor_xpath)
        if len(documents) >= 0:
            return [
                {
                    "href": response.urljoin(document.xpath("@href").extract_first()),
                    "title": document.xpath("text()").extract_first(),
                }
                for document in documents
            ]
        return []
