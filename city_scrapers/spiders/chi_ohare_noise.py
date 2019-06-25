from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Request
import datetime


class ChiOhareNoiseSpider(CityScrapersSpider):
    name = "chi_ohare_noise"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.oharenoise.org"]
    meetings = dict()
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
                date = self._parse_start(item)
                url_date = date.strftime("%Y/%m/%d")
                meeting = Meeting(
                    # Meeting title will always be second column
                    title=self._parse_title(item),
                    links=self._parse_links(item),
                    start=self._parse_start(item),
                    source=self._parse_source(response)
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                self.meetings[url_date] = meeting
        else:
            curr_date = datetime.date.today()
            months_urls = [datetime.date(month=curr_date.month-2, day=1, year=curr_date.year),
                           datetime.date(month=curr_date.month-1, day=1, year=curr_date.year),
                           curr_date,
                           datetime.date(month=curr_date.month+1, day=1, year=curr_date.year)
                           ]
            for date in months_urls:
                yield Request(
                        "https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/" +
                        date.strftime("%Y/%m/%d"), self._parse_calendar)

    def _parse_calendar(self, response):
        event_urls = response.selector.xpath(".//a[@class='cal_titlelink']//@href").extract()
        for event_url in event_urls:
            yield Request("https://www.oharenoise.org" + event_url, self._parse_event)

    def _parse_event(self, response):
        info_body = response.selector.xpath(".//div[@id='jevents_body']")
        name_date_time = info_body.xpath(".//div[@class='jev_evdt_header']")
        name = name_date_time.xpath(".//h2/text()").get()
        date_time = name_date_time.xpath(".//p/text()").extract()
        event_date = datetime.datetime.strptime(date_time[0], "%A, %B %d, %Y")
        event_time = datetime.datetime.strptime(date_time[1].strip(), "%I:%M%p")
        event_date = event_date.replace(hour=event_time.hour, minute=event_time.minute)
        date_key = event_date.strftime("%Y/%m/%d")
        description = info_body.xpath(".//div[@class='jev_evdt_desc']//p/text()").get()
        location = info_body.xpath(".//div[@class='jev_evdt_location']/text()").get()
        if date_key in self.meetings:
            meeting = self.meetings[date_key]
            meeting['start'] = event_date


    def _parse_title(self, item, is_calen=False):
        """Parse or generate meeting title."""
        if is_calen:
            print("calen")
        else:
            return item.xpath(".//td[@class='djc_category']/span/text()").get()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item, is_calen=False):
        """Parse start datetime as a naive datetime object."""
        if is_calen:
            print("calen start")
        else:
            date = item.xpath(".//td[@class='djc_producer']/span/text()").get()
            return datetime.datetime.strptime(date, "%B %d, %Y")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate allday status. Defaults to False."""
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
