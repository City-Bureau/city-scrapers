from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlAgingAdvisoryCouncilSpider(CityScrapersSpider):
    name = "il_aging_advisory_council"
    agency = "Illinois Aging Advisory Council"
    timezone = "America/Chicago"
    start_urls = [
        "https://www2.illinois.gov/aging/PartnersProviders/OlderAdult/Pages/acmeetings.aspx"  # noqa
    ]
    location = {
        "address": "160 N. LaSalle Street, 7th Floor, Chicago",
        "name": "Michael A. Bilandic Building",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self._validate_location(response)

        self._validate_meeting_times(response)

        table = response.xpath(
            '//*[@id="ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField"]\
            /table'
        )

        for table_row in table.xpath(".//tr"):
            row_date = table_row.xpath(
                ".//strong/\
            text()"
            ).re(r"([A-Z]\w+)\s*(\d\d?),*\s*(\d\d\d\d)")
            if not row_date:
                continue
            converted_date = self._convert_date(row_date)

            row_urls = table_row.xpath(".//a")

            meeting = Meeting(
                title="Advisory Committee",
                description="",
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(converted_date),
                end=self._parse_end(converted_date),
                all_day=self._parse_all_day(table_row),
                time_notes="",
                location=self.location,
                links=self._parse_links(row_urls),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _validate_location(self, response):
        location_test = response.xpath(
            '//*[@id="ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField"]\
        /ul/li[2]/text()'
        ).get()
        if "7th Floor, 160 N. LaSalle Street" not in location_test:
            raise ValueError("Meeting location has changed")

    def _validate_meeting_times(self, response):
        meeting_time = response.xpath(
            '//*[@id="ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField"]\
        /p[1]/text()'
        ).get()
        if "1 p.m. - 3 p.m" not in meeting_time:
            raise ValueError("Meeting times have changed")

    def _convert_date(self, item):
        """Parse start datetime as a naive datetime object."""
        month = item[0]
        day = item[1]
        year = item[2]
        converted_date = datetime.strptime(month[0:3] + day + year, "%b%d%Y")
        return converted_date

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return item.replace(hour=13)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return item.replace(hour=15)

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        for i in item:
            href = i.xpath("@href").get()
            if not href:
                continue
            full_href = "https://www2.illinois.gov" + href
            text = i.xpath("text()").get()
            if not text:
                continue
            stripped_text = text.replace("\u200b", "").replace("\xa0", "")
            links.append({"href": full_href, "title": stripped_text})
        return links

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
