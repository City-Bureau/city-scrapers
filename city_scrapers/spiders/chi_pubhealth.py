import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiPubHealthSpider(CityScrapersSpider):
    name = "chi_pubhealth"
    agency = "Chicago Department of Public Health"
    timezone = "America/Chicago"

    @property
    def start_urls(self):
        """
        DPH generally uses a standard URL format, but sometimes deviates from
        the pattern. This property inserts the current year into the standard
        format, as well as known variants, in hopes DPH sticks to one of their
        conventions and this scraper does not need to be updated annually.
        """
        standard_url = "https://www.chicago.gov/city/en/depts/cdph/supp_info/boh/{}-board-of-health-meetings.html"  # noqa
        url_variant_1 = "https://www.chicago.gov/city/en/depts/cdph/supp_info/boh/{}-board-of-health.html"  # noqa

        current_year = datetime.now().year

        return [
            standard_url.format(current_year),
            url_variant_1.format(current_year),
        ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        title = response.xpath('//h1[@class="page-heading"]/text()').extract_first()

        # Extract year and meeting name from title like "2017 Board of Health Meetings"
        parts = re.match(r"(\d{4}) (.*?)s", title)
        self.year = int(parts.group(1))
        title = parts.group(2)

        # The description and meeting dates are a series of p elements
        p = response.xpath(
            '//div[contains(@class, "page-full-description-above")]/div/div/p'
        )

        for idx, item in enumerate(p, start=1):

            if idx == 1:
                # Description is the first p element
                description = item.xpath("text()").extract_first()
                if "333 S" not in description:
                    raise ValueError("Meeting location has changed")
                continue

            # Skip empty rows
            if not item.css("*::text").extract_first().strip():
                continue

            meeting = Meeting(
                title=title,
                description="",
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                time_notes="",
                all_day=False,
                location={
                    "name": "2nd Floor Board Room, DePaul Center",
                    "address": "333 S State St, Chicago, IL 60604",
                },
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(
                meeting, text=" ".join(item.css("*::text").extract())
            )
            yield meeting

    def _parse_date(self, item):
        """
        Parse the meeting date.
        """
        # Future meetings are plain text
        date_text = (item.xpath("text()").extract_first() or "").strip()

        if not date_text:
            # Past meetings are links to the agenda
            date_text = item.xpath("a/text()").extract_first()

        # Remove extra whitespace characters
        date_text = re.sub(r"\s+", " ", date_text).strip()

        # Handle typos like "December18"
        if re.match(r"[a-zA-Z]+\d+", date_text):
            date_match = re.search(r"(?P<month>[a-zA-Z]+)(?P<day>\d+)", date_text)
            date_text = "{} {}".format(
                date_match.group("month"), date_match.group("day")
            )
        # Extract date formatted like "January 12"
        return datetime.strptime(date_text, "%B %d")

    def _parse_start(self, item):
        """
        Parse the meeting date and set start time to 9am.
        """
        datetime_obj = self._parse_date(item)
        return datetime(self.year, datetime_obj.month, datetime_obj.day, 9)

    def _parse_links(self, item, response):
        """
        Parse agenda and minutes, if available.
        """
        documents = []

        agenda_relative_url = item.xpath("a/@href").extract_first()
        if agenda_relative_url:
            documents.append(
                {"href": response.urljoin(agenda_relative_url), "title": "Agenda"}
            )

        minutes_relative_url = item.xpath(
            "following-sibling::ul/li/a/@href"
        ).extract_first()
        if minutes_relative_url:
            documents.append(
                {"href": response.urljoin(minutes_relative_url), "title": "Minutes"}
            )
        return documents
