import datetime
import re

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlPortDistrictSpider(CityScrapersSpider):
    name = "il_port_district"
    agency = "Illinois International Port District"
    timezone = "America/Chicago"
    allowed_domains = ["www.iipd.com"]
    location = {
        "name": "Illinois International Port District ",
        "address": "3600 E. 95th St. Chicago, IL 60617",
    }

    schedules_url = "https://www.iipd.com/calendar/schedules"

    def start_requests(self):
        start_urls = [
            "https://www.iipd.com/calendar/agendas",
            "https://www.iipd.com/about/board-meeting-minutes"
        ]
        for url in start_urls:
            if url == start_urls[0]:
                yield scrapy.Request(url=url, callback=self.parse_agendas)
            if url == start_urls[1]:
                yield scrapy.Request(url=url, callback=self.parse_minutes)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def spider_idle(self):
        """Call parse_schedules if spider is idle (finished parsing minutes and agendas)"""
        self.crawler.signals.disconnect(self.spider_idle, signal=scrapy.signals.spider_idle)
        self.crawler.engine.crawl(
            scrapy.Request(self.schedules_url, callback=self.parse_schedules), self
        )
        raise scrapy.exceptions.DontCloseSpider

    def parse_schedules(self, response):

        year = response.xpath("//em/text()").extract_first()[:4]

        rows = response.xpath("//tr")
        meeting_types = rows[0].xpath(".//strong/text()").extract()
        meeting_types = [x.strip(" :s") for x in meeting_types]

        strong_meetings = rows.xpath(".//strong/text()")[len(meeting_types):].extract()
        if len(strong_meetings) % 2 != 0:
            strong_meetings.append('')
        strong_meetings = list(zip(strong_meetings[0::2], strong_meetings[1::2]))

        additional_info = response.xpath("//p[contains(text(), '*')]/text()").extract()
        changed_meeting_time = re.findall(r"\d{1,2}:\d{2}am|pm", additional_info[2])[0]
        meeting_time = "9:00am"

        self._validate_location(response)

        for i, row in enumerate(strong_meetings + rows[1:]):
            if i >= len(strong_meetings):
                meetings_dates = row.xpath(".//div/text()").extract()
                if not meetings_dates:
                    continue
            else:
                meetings_dates = row

            for i, date in enumerate(meetings_dates):
                if not date:
                    continue
                special_meeting = None
                if date.startswith("***") or date.endswith("***"):
                    meeting_time = changed_meeting_time
                elif date.startswith("**") or date.endswith("**"):
                    special_meeting = "Special "
                elif date.startswith("*") or date.endswith("*"):
                    new_date = re.findall(r"(?<=\()(.*?)(?=NEW)", date)
                    date = new_date[0][:-3] if new_date else date

                date = date.strip(" *")

                title = meeting_types[i] if not special_meeting\
                    else special_meeting + meeting_types[i]

                classification = self._parse_classification(i, meeting_types[i])

                start = self._parse_start(year, date, meeting_time)

                agendas_links = self._parse_agendas_links(classification)

                minutes_links = None

                if classification == "Board":
                    minutes_links = self._parse_minutes_links(start)
                links = agendas_links if not minutes_links else\
                    agendas_links + minutes_links

                meeting = Meeting(
                    title=title,
                    description="",
                    classification=classification,
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self.location,
                    links=links,
                    source=response.url
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def parse_agendas(self, response):
        file_names = response.xpath("//tr/td[@class='views-field views-field-title']/text()")\
            .extract()
        file_names = [x.strip("\n ") for x in file_names]
        file_links = response.xpath("//tr/td/a[@class='file-download']/@href").extract()

        self.files_list = []

        for link, name in list(zip(file_links, file_names)):
            self.files_list.append({'title': name, 'href': link})

    def parse_minutes(self, response):
        rows = response.xpath("//tr")
        self.minutes_dict = {}
        for row in rows:
            file_name = row.xpath(".//td[@class='views-field views-field-title']/text()")\
                .extract_first()
            if not file_name:
                continue

            file_name = file_name.strip("\n ")
            file_name_dt = re.findall(r"(?:.*?)(?:\d{4})", file_name)[0]
            file_name_dt = datetime.datetime.strptime(file_name_dt, "%B %d, %Y")

            file_link = row.xpath(".//td[@class='views-field views-field-field-file']/a/@href")\
                .extract_first()

            self.minutes_dict.setdefault(file_name_dt.date(), file_link)

    def _parse_classification(self, i, meeting_types):
        if "board" in meeting_types.lower():
            return BOARD
        elif "committee" in meeting_types.lower():
            return COMMITTEE
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, year, date, meeting_time):
        dt = " ".join([year, date, meeting_time])
        return datetime.datetime.strptime(dt, "%Y %B %d %I:%M%p")

    def _parse_agendas_links(self, classification):
        if classification == 'Board':
            link_list = [d for d in self.files_list if 'Board' in d['title']]
        elif classification == 'Committee':
            link_list = [d for d in self.files_list if 'Committee' in d['title']]
        else:
            link_list = []

        return link_list

    def _parse_minutes_links(self, start):
        link = self.minutes_dict.get(start.date(), None)
        if link:
            name = "Board Meeting Minutes"
            return [{'title': name, 'href': link}]
        else:
            return None

    def _validate_location(self, response):
        loc = response.xpath("//strong")[-1].xpath(".//text()").extract()
        loc = [x.strip("\n ") for x in loc]
        loc = " ".join(loc[-2:])
        if '3600 E. 95th St. Chicago, IL 60617' != loc:
            raise ValueError("Meeting location has changed")
