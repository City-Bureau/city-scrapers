import re
from datetime import datetime, time

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiCommunityDevelopmentSpider(CityScrapersSpider):
    name = "chi_community_development"
    agency = "Chicago Community Development Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://chicago.gov/city/en/depts/dcd/supp_info/community_developmentcommission.html"  # noqa
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
            year = column.xpath("preceding::h3[1]/text()").re_first(r"(\d{4})(.*)")
            meeting_date_xpath = "text()[normalize-space()]|p/text()[normalize-space()]"
            items = column.xpath(meeting_date_xpath).extract()
            items = self.format_meetings(items)
            for item in items:
                start = self._parse_start(item, year)
                if start < last_year and not self.settings.getbool(
                    "CITY_SCRAPERS_ARCHIVE"
                ):
                    continue
                meeting = Meeting(
                    title="Commission",
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    time_notes="",
                    all_day=False,
                    location={
                        "name": "City Hall",
                        "address": "121 N LaSalle St, Room 201A, Chicago, IL 60602",
                    },
                    source=response.url,
                    links=self._parse_links(column, item, response),
                )
                meeting["id"] = self._get_id(meeting)
                meeting["status"] = self._get_status(meeting, text=item)
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
                //td[preceding::h3[1]/text()[
                    contains(., "Meeting Schedule")
                    ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_start(meeting, year):
        m = re.search(r"(?P<month>\w+)\.?\s(?P<day>\d+).*", meeting.strip())
        dt = dateutil.parser.parse(
            "{mo} {day} {year}".format(
                mo=m.group("month"), day=m.group("day"), year=year
            )
        )
        return datetime.combine(dt.date(), time(13))

    def _parse_links(self, item, meeting, response):
        # Find <a> tags where 1st, non-blank, preceding text = meeting
        #  (e.g. 'Jan 16')
        anchor_xpath = (
            "a[preceding-sibling::text()[normalize-space()]" '[1][contains(., "{}")]]'
        ).format(meeting)
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
