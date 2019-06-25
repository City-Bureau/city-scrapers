from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import datetime
import time

class ChiOhareNoiseSpider(CityScrapersSpider):
    name = "chi_ohare_noise"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.oharenoise.org"]
    start_urls = ["https://www.oharenoise.org/about-oncc/agendas-and-minutes",
                  "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if "agendas" in response.url:

            table_rows = response.selector.xpath(".//tbody//tr")
            for item in table_rows:

                meeting = Meeting(
                    # Meeting title will always be second column
                    title=self._parse_title(item),
                    start=self._parse_start(item),
                    links=self._parse_links(item),
                    source=self._parse_source(response)
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting
        else:
            event_days = response.selector.xpath(".//td[@class='cal_dayshasevents']")
            for item in event_days:
                date = item. \
                        xpath(".//a[@class='cal_daylink']//span[@class='listview']/text()"). \
                        get(). \
                        lstrip()
                events = item.xpath(".//a[@class='cal_titlelink']")
                for event in events:

                    time = event.xpath(".//span/text()").get()
                    name = event.xpath("text()").get()
                    print(date)
                    print(name.split()[0].isupper())
                    print(time)

    def convert_date(self, date_str):
        date_str = datetime.strptime(date_str, "%b %d, %Y")
        return date_str

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.xpath(".//td[@class='djc_category']/span/text()").get()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.xpath(".//td[@class='djc_producer']/span/text()").get()
        return datetime.datetime.strptime(date, "%B %d, %Y")

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
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        agenda_minute = item.xpath(".//li[@class='djc_file']")
        agenda_href = agenda_minute[0].xpath(".//a/@href").get()
        minute_href = agenda_minute[1].xpath(".//a/@href").get()

        links = []
        if agenda_href is not None:
            links.append({"href": agenda_href, "title": "Agenda"})

        if minute_href is not None:
            links.append({"href": minute_href, "title": "Minutes"})

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
