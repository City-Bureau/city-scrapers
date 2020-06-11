from datetime import datetime as dt

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

HOUR_DICT = {"a": "am", "am": "am", "p": "pm", "pm": "pm"}


class ChiSsa72Spider(CityScrapersSpider):
    name = "chi_ssa_72"
    agency = "Chicago Special Service Area #72 Austin"
    timezone = "America/Chicago"
    start_urls = ["http://www.av72chicago.com/commissioners--meetings.html"]
    location = {
        "address": "5053 W. Chicago Ave, Chicago, IL, 60651",
        "name": "Westside Health Authority",
    }
    title = "Advisory Commission"

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        year = response.xpath("//u/font/strong/em/text()").get()[0:4]
        for item in response.xpath("//ol/li"):
            date_text = item.xpath("./font/strong/em/text()").get()
            meeting = Meeting(
                title=self.title,
                description="",
                classification=COMMISSION,
                start=self._parse_start(date_text, year),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting, text=date_text)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, date_text, year):
        """Parse start datetime as a naive datetime object."""

        def _date_helper(text):
            day_str_with_suffix, time_str_raw = stripped_text.split(",")
            day_str = day_str_with_suffix[:-2]
            day_str = day_str.replace("Sept", "Sep") if "Sept" in day_str else day_str
            time_str = time_str_raw.replace(
                time_str_raw[-1], HOUR_DICT[time_str_raw[-1]]
            )
            date_str = year + day_str + time_str
            date_dt_obj = dt.strptime(date_str, "%Y%A-%b%d%I%p")
            return date_dt_obj

        if "(Time Changed to " in date_text:
            stripped_text_day, stripped_text_time = date_text.split("(Time Changed to")
            text_day = stripped_text_day.split(",")[0].replace(" ", "")[:-2]
            text_time = stripped_text_time.split(")")[0]
            return dt.strptime(year + text_day + text_time, "%Y%A-%B%d %I:%M%p")

        if "(replaces)" in date_text:
            stripped_text_day, stripped_text_time = date_text.split(" (replaces) ")
            weekday = stripped_text_day.split(" - ")[0]
            stripped_month, stripped_hour = stripped_text_time.split(", ")
            month = stripped_month[:-2]
            hour = stripped_hour.replace(
                stripped_hour[-1], HOUR_DICT[stripped_hour[-1]]
            )
            time_str = year + weekday + month + hour
            return dt.strptime(time_str, "%Y%A%B %d%I%p")

        if "Canceled" in date_text:
            stripped_text = date_text.replace("(Canceled)", "").replace(" ", "")
        elif "|" in date_text:
            stripped_text = date_text.split("|")[0].replace(" ", "")
        else:
            stripped_text = date_text.replace(" ", "")

        return _date_helper(stripped_text)

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = item.xpath("./font/strong/em/a")
        if links:
            return [
                {
                    "href": response.urljoin(link.xpath("./@href").get()),
                    "title": link.xpath("./text()").get(),
                }
                for link in links
            ]
        return []
