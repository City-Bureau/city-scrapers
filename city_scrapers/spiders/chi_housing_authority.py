import re
from datetime import datetime, time, timedelta

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiHousingAuthoritySpider(CityScrapersSpider):
    name = "chi_housing_authority"
    agency = "Chicago Housing Authority"
    timezone = "America/Chicago"
    start_urls = [
        "http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-information-and-meetings",  # noqa
    ]
    location = {
        "name": "CHA Corporate Offices",
        "address": "60 E Van Buren St, 7th Floor, Chicago, IL 60605",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if "60 East Van Buren" not in response.text:
            raise ValueError("Meeting address has changed")

        self.upcoming_meetings = self._parse_upcoming(response)
        yield scrapy.Request(
            "http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-meeting-notices",  # noqa
            callback=self._parse_next,
            dont_filter=True,
        )

    def _parse_next(self, response):
        """Chains previous requests and yields a request to combine all results"""
        req = scrapy.Request(
            "http://www.thecha.org/doing-business/contracting-opportunities/view-all/Board%20Meeting",  # noqa
            callback=self._parse_combined_meetings,
            dont_filter=True,
        )
        self.upcoming_meetings = self._parse_notice(response)
        yield req

    def _parse_upcoming(self, response):
        """
        Returns a list of dicts including the start date, status for upcoming meetings
        """
        year_title = response.css(
            ".text-area-full h2.text-align-center *::text"
        ).extract_first()
        upcoming_year = re.search(r"^\d{4}", year_title).group(0)
        date_list = []
        # Get list of month names to check in regular expression
        months = [
            datetime(int(upcoming_year), i, 1).strftime("%B") for i in range(1, 13)
        ]
        for item in response.css(".text-area-full table.text-align-center td *::text"):
            item_text = item.extract()
            # See if text matches date regex, if so add to list
            date_match = re.search(
                r"({}) \d{{1,2}}".format("|".join(months)), item.extract()
            )
            if date_match:
                date_str = "{} {}".format(date_match.group(), upcoming_year)
                date_dict = {
                    "start": datetime.strptime(date_str, "%B %d %Y"),
                    "source": response.url,
                }
                date_dict["status"] = self._get_status(date_dict, text=item_text)
                date_list.append(date_dict)
        return date_list

    def _parse_notice(self, response):
        """Returns a list of meetings with notice documents added to applicable dates"""
        notice_documents = self._parse_notice_documents(response)
        meetings_list = []
        for meeting in self.upcoming_meetings:
            # Check if the meeting date is in any document title, assign docs if so
            meeting_date_str = "{dt:%B} {dt.day}".format(dt=meeting["start"])
            if any(meeting_date_str in doc["title"] for doc in notice_documents):
                meetings_list.append(
                    {**meeting, "links": notice_documents, "source": response.url}
                )
            else:
                meetings_list.append({**meeting, "links": []})
        return meetings_list

    def _parse_notice_documents(self, response):
        """Get document links from notice page, ignoring mailto and flyer links"""
        notice_documents = []
        for doc in response.css("article.full a[href]"):
            doc_text = doc.css("*::text").extract_first()
            if "mailto" in doc.attrib["href"] or "flyer" in doc_text.lower():
                continue
            notice_documents.append(
                {"href": response.urljoin(doc.attrib["href"]), "title": doc_text}
            )
        return notice_documents

    def _parse_combined_meetings(self, response):
        """Combines upcoming and past meetings and yields results ignoring duplicates"""
        meetings = self._parse_past_meetings(response)
        meeting_dates = set([meeting["start"] for meeting in meetings])

        for meeting in self.upcoming_meetings:
            if meeting["start"] not in meeting_dates:
                meetings.append(meeting)

        six_months_ago = datetime.now() - timedelta(days=180)
        for item in meetings:
            if item["start"] < six_months_ago and not self.settings.getbool(
                "CITY_SCRAPERS_ARCHIVE"
            ):
                continue
            meeting = Meeting(
                title="Board of Commissioners",
                description="",
                classification=BOARD,
                start=datetime.combine(item["start"].date(), time(8, 30)),
                end=datetime.combine(item["start"].date(), time(13)),
                time_notes="Times may change based on notice",
                all_day=False,
                location=self._parse_location(item["start"]),
                links=item["links"],
                source=item.get("source", response.url),
            )
            meeting["status"] = item.get("status", self._get_status(meeting))
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_past_meetings(self, response):
        """Returns a list of start date and documents from meeting minutes page"""
        meetings = []
        for item in response.css("table.table-striped tbody tr"):
            dt_str = item.css("time::text").extract_first()
            meetings.append(
                {
                    "start": datetime.strptime(dt_str, "%b %d, %Y"),
                    "links": self._parse_past_documents(item, response),
                }
            )
        return meetings

    def _parse_past_documents(self, item, response):
        """Returns all documents for a past meeting"""
        doc_list = []
        for doc in item.css("a"):
            doc_list.append(
                {
                    "href": response.urljoin(doc.attrib["href"]),
                    "title": doc.css("*::text").extract_first(),
                }
            )
        return doc_list

    def _parse_location(self, start):
        """Meeting locations changed in 2020, return old address if before that"""
        if start.year < 2020:
            return {
                "name": "Charles A. Hayes FIC",
                "address": "4859 S Wabash Chicago, IL 60615",
            }
        return self.location
