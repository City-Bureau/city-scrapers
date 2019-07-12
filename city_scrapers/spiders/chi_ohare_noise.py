from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import datetime


class ChiOhareNoiseSpider(CityScrapersSpider):
    name = "chi_ohare_noise"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.oharenoise.org"]
    meetings = dict()
    start_urls = ["https://www.oharenoise.org/about-oncc/agendas-and-minutes"]
    requests = []

    def parse(self, response):

        """
        `parse` should always `yield` Meeting items.
        """
        table_rows = response.selector.xpath(".//tbody//tr")

        for item in table_rows:
            date = self._parse_start(item)
            url_date = date.strftime("%Y/%m/%d")
            meeting = Meeting(
                title=self._parse_title(item),
                links=self._parse_links(item),
                start=self._parse_start(item),
                source=self._parse_source(response)
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            self.meetings[url_date] = meeting

            self._parse_months()
            for date, meeting in self.meetings.items():
                yield meeting

    def _parse_months(self):
        curr_date = datetime.date.today()
        months_urls = [datetime.date(month=curr_date.month-2, day=1, year=curr_date.year),
                       datetime.date(month=curr_date.month-1, day=1, year=curr_date.year),
                       curr_date,
                       datetime.date(month=curr_date.month+1, day=1, year=curr_date.year)
                       ]
        for date in months_urls:
            self._parse_calendar(HtmlResponse(
                    url="https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/" +
                    date.strftime("%Y/%m/%d")))

    def _parse_calendar(self, response):
        response = Selector(response=response)
        event_urls = response.xpath(".//a[@class='cal_titlelink']//@href")
        for event_url in event_urls:
            self._parse_event(HtmlResponse(url="https://www.oharenoise.org" + event_url))

    def _parse_event(self, response):
        response = Selector(response.content)
        info_body = response.xpath(".//div[@id='jevents_body']")
        name_date_time = info_body.xpath(".//div[@class='jev_evdt_header']")
        start = self._parse_start(name_date_time, is_calen=True)
        date_key = start.strftime("%Y/%m/%d")
        description = self._parse_description(info_body)
        location = self._parse_location(info_body)
        meeting = None
        if date_key in self.meetings:
            meeting = self.meetings[date_key]
            meeting['start'] = start
            meeting['description'] = description
            meeting['location'] = location
        else:
            meeting = Meeting(
                    title=self._parse_title(name_date_time, is_calen=True),
                    start=start,
                    description=description,
                    location=location
                    )
            self.meetings[date_key] = meeting

    def _not_empty(self, string):
        if string is not None and not str.isspace(string):
            return True
        else:
            return False

    def _parse_title(self, item, is_calen=False):
        """Parse or generate meeting title."""
        if is_calen:
            title = item.xpath(".//h2/text()").get()
            return title if self._not_empty(title) else None
        else:
            title = item.xpath(".//td[@class='djc_category']/span/text()").get()
            return title if self._not_empty(title) else None

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        description = item.xpath(".//div[@class='jev_evdt_desc']//p/text()").get()
        extra_info = item.xpath(".//div[@class='jev_evdt_extrainf']/text()").get()
        if self._not_empty(extra_info):
            description = description + extra_info

        return description if self._not_empty(description) else None

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item, is_calen=False):
        """Parse start datetime as a naive datetime object."""
        if is_calen:
            date_time = item.xpath(".//p/text()").extract()
            event_date = datetime.datetime.strptime(date_time[0], "%A, %B %d, %Y")
            event_time = datetime.datetime.strptime(date_time[1].strip(), "%I:%M%p")
            event_date.replace(hour=event_time.hour, minute=event_time.minute)
            return event_date
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
        location = item.xpath(".//div[@class='jev_evdt_location']/text()").get()
        location_array = location.split(',')
        if self._not_empty(location):
            return {
                "address": location,
                "name": location_array[0],
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
