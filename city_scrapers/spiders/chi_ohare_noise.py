import datetime

import requests
from city_scrapers_core import constants
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.selector import Selector


class ChiOhareNoiseSpider(CityScrapersSpider):
    name = "chi_ohare_noise"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.oharenoise.org"]
    # meetings is indexed in the format meetings[meeting_title + " " + meeting_date]
    meetings = dict()
    start_urls = ["https://www.oharenoise.org/about-oncc/agendas-and-minutes"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        loops through agenda/minutes page and compiles all agenda and minutes pdfs to links
        parses current month, last two months, and next month calendars for meetings
        """
        table_rows = response.selector.xpath(".//tbody//tr")

        for item in table_rows:
            date = self._parse_start(item)
            url_date = date.strftime("%Y/%m/%d")
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                links=self._parse_links(item),
                start=self._parse_start(item),
                source=self._parse_source(response)
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            dict_key = title + " " + url_date
            self.meetings[dict_key] = meeting

        self._parse_months()
        for date, meeting in self.meetings.items():
            yield meeting

    def _parse_months(self):
        """
        generates list of calendar links and requests them
        """
        curr_date = datetime.date.today()
        months_urls = [
            datetime.date(
                month=self._delta_months(curr_date.month, -2), day=1, year=curr_date.year
            ),
            datetime.date(
                month=self._delta_months(curr_date.month, -1), day=1, year=curr_date.year
            ), curr_date,
            datetime.date(month=self._delta_months(curr_date.month, 1), day=1, year=curr_date.year)
        ]
        for calendar_date in months_urls:
            self._parse_calendar(
                requests.get(
                    url="https://www.oharenoise.org/about-oncc/oncc-meetings/month.calendar/" +
                    calendar_date.strftime("%Y/%m/%d")
                )
            )

    def _parse_calendar(self, body):
        """
        finds all events on calendar and requests detail pages
        """
        selector = Selector(text=body.text)
        event_urls = selector.xpath(".//a[@class='cal_titlelink']//@href").extract()
        for event_url in event_urls:
            self._parse_event(requests.get(url="https://www.oharenoise.org" + event_url))

    def _parse_event(self, body):
        """
        parses detail page for
        date, status, all_day, classification, description, location, and title
        """
        selector = Selector(text=body.text)
        info_body = selector.xpath(".//div[@id='jevents_body']")
        name_date_time = info_body.xpath(".//div[@class='jev_evdt_header']")
        start = self._parse_start(name_date_time, is_calen=True)
        date = start.strftime("%Y/%m/%d")
        description = self._parse_description(info_body)
        location = self._parse_location(info_body)
        meeting = None
        title = self._parse_title(name_date_time, is_calen=True)
        classification = self._parse_classification(title)
        dict_key = title + " " + date
        if dict_key in self.meetings:
            meeting = self.meetings[dict_key]
            meeting['title'] = title
            meeting['all_day'] = False
            meeting['start'] = start
            meeting['description'] = description
            meeting['location'] = location
            meeting['classification'] = classification
            meeting['status'] = self._get_status(meeting)
        else:
            meeting = Meeting(
                title=title,
                start=start,
                classification=classification,
                description=description,
                location=location,
                all_day=False
            )
            meeting['status'] = self._get_status(meeting)
            self.meetings[dict_key] = meeting

    def _parse_title(self, item, is_calen=False):
        """Parse or generate meeting title."""
        if is_calen:
            title = item.xpath(".//h2/text()").get()
            return title if title else None
        else:
            title = item.xpath(".//td[@class='djc_category']/span/text()").get()
            return title if title else None

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        description = item.xpath(".//div[@class='jev_evdt_desc']//p/text()").get()
        extra_info = item.xpath(".//div[@class='jev_evdt_extrainf']/text()").get()
        if extra_info:
            description = description + extra_info

        return description if description else ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        result = constants.NOT_CLASSIFIED
        if constants.ADVISORY_COMMITTEE in item:
            result = constants.ADVISORY_COMMITTEE
        elif constants.BOARD in item:
            result = constants.BOARD
        elif constants.CITY_COUNCIL in item:
            result = constants.CITY_COUNCIL
        elif constants.COMMISSION in item:
            result = constants.COMMISSION
        elif constants.COMMITTEE in item:
            result = constants.COMMITTEE
        elif constants.FORUM in item:
            result = constants.FORUM
        elif constants.POLICE_BEAT in item:
            result = constants.POLICE_BEAT

        return result

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
        if location:
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

    def _delta_months(self, curr, delta):
        """
        handles add and subtracting from months
        """
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        new = (curr - 1) + delta
        return months[new % 12]
