from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa35Spider(CityScrapersSpider):
    name = "chi_ssa_35"
    agency = "Chicago Special Service Area #35 Lincoln Ave"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.lincolnparkchamber.com/"
        + "businesses/special-service-areas/lincoln-avenue-ssa/ssa-administration/"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        content_div = response.css("div.content_block.content.background_white")
        dates = content_div.css("ol").css("li::text").getall()
        dates = self._add_year_to_date_item(dates)

        urls = content_div.css("a")
        content = list(zip(dates, urls[: len(dates)]))

        for item in content:
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Commission"

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _add_year_to_date_item(self, date_items):
        new_dates = []
        current_year = datetime.today().year + 1

        for item in date_items:
            if "January" in item:
                current_year -= 1
                new_dates.append(f"{item} {current_year}")
            else:
                new_dates.append(f"{item} {current_year}")
        return new_dates

    def _clean_date_item(self, date_item):
        date_item = date_item.split()

        if len(date_item) == 6:
            date_item[-2] = date_item[-2].replace(")", "")
            date_item[-3] = date_item[-3].replace("(", "")

        elif len(date_item) == 4:
            date_item.insert(len(date_item) - 1, "09:00 am")

        del date_item[0]
        return " ".join(date_item)

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_item = self._clean_date_item(item[0])
        date_obj = datetime.strptime(date_item, "%B %d %I:%M %p %Y")

        return date_obj

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "Confirm with agency",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        href = item[1].css("::attr(href)").get()
        title = item[1].css("::text").get()

        return [{"href": href, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
