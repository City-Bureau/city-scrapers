import re
from collections import defaultdict
from datetime import datetime

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
        yield scrapy.Request(
            url="https://www.iipd.com/calendar/agendas", callback=self.parse_agendas
        )
        yield scrapy.Request(
            url="https://www.iipd.com/about/board-meeting-minutes",
            callback=self.parse_minutes,
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def spider_idle(self):
        """
        Call parse_schedules if spider is idle (finished parsing minutes and agendas)
        """
        self.crawler.signals.disconnect(
            self.spider_idle, signal=scrapy.signals.spider_idle
        )
        self.crawler.engine.crawl(
            scrapy.Request(self.schedules_url, callback=self.parse_schedules), self
        )
        raise scrapy.exceptions.DontCloseSpider

    def parse_schedules(self, response):
        year = response.css(".rtecenter em::text").extract_first()[:4]

        rows = response.xpath("//tr")
        meeting_types = rows[0].xpath(".//strong/text()").extract()
        meeting_types = [x.strip(" :s") for x in meeting_types]

        strong_meetings = rows.xpath(".//strong/text()")[len(meeting_types) :].extract()
        if len(strong_meetings) % 2 != 0:
            strong_meetings.append("")
        strong_meetings = list(zip(strong_meetings[0::2], strong_meetings[1::2]))

        additional_info = response.xpath("//p[contains(text(), '*')]/text()").extract()
        changed_meeting_time = re.findall(r"\d{1,2}:\d{2}am|pm", additional_info[2])[0]

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

                start = self._parse_start(date, year, changed_meeting_time)

                title = self._parse_title(date, meeting_types[i])

                classification = self._parse_classification(i, meeting_types[i])

                agendas_links = self.agendas_dict.get(
                    (classification, start.strftime("%B %Y")), []
                ) + self.agendas_dict.get(
                    (classification, start.strftime("%-m-%y")), []
                )

                minutes_links = []

                if classification == BOARD:
                    minutes_links = self.minutes_dict.get(start.date(), [])

                links = agendas_links + minutes_links

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
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def parse_agendas(self, response):
        file_names = response.xpath(
            "//tr/td[@class='views-field views-field-title']/text()"
        ).extract()
        file_names = [x.strip("\n ") for x in file_names]
        file_links = response.xpath("//tr/td/a[@class='file-download']/@href").extract()
        agenda_file_groups = []
        for idx, file_link in enumerate(file_links):
            clean_link = file_link.replace("%20", " ")
            # Check two possible URL formats for agenda date patterns
            agenda_date_match_1 = re.search(r"([\d\-]+).*?(?=.pdf)", clean_link)
            agenda_date_match_2 = re.search(r"(?<=Agenda)(.*?)(?=.pdf)", clean_link)
            if agenda_date_match_1:
                agenda_file_groups.append(
                    (file_link, file_names[idx], agenda_date_match_1.group(1))
                )
            if agenda_date_match_2:
                agenda_file_groups.append(
                    (file_link, file_names[idx], agenda_date_match_2.group().strip())
                )
        self.agendas_dict = defaultdict(list)

        for link, name, agenda_date in agenda_file_groups:
            classification = BOARD if BOARD in name else COMMITTEE
            self.agendas_dict[(classification, agenda_date.strip())].append(
                {"title": " ".join([name, agenda_date]), "href": link}
            )

    def parse_minutes(self, response):
        rows = response.xpath("//tr")
        self.minutes_dict = {}
        for row in rows:
            file_name = row.xpath(
                ".//td[@class='views-field views-field-title']/text()"
            ).extract_first()
            if not file_name:
                continue

            file_name = file_name.strip("\n ")
            file_name_dt = re.findall(r"(?:.*?)(?:\d{4})", file_name)[0]
            file_name_dt = datetime.strptime(file_name_dt, "%B %d, %Y")

            file_link = row.xpath(
                ".//td[@class='views-field views-field-field-file']/a/@href"
            ).extract_first()

            self.minutes_dict.setdefault(
                file_name_dt.date(),
                [{"title": "Board Meeting Minutes", "href": file_link}],
            )

    def _parse_classification(self, i, meeting_types):
        if BOARD in meeting_types:
            return BOARD
        elif COMMITTEE in meeting_types:
            return COMMITTEE
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, date, year, changed_meeting_time):
        meeting_time = "9:00am"

        if date.startswith("***") or date.endswith("***"):
            meeting_time = changed_meeting_time
        elif date.startswith("*") or date.endswith("*"):
            new_date = re.findall(r"(?<=\()(.*?)(?=NEW)", date)
            date = new_date[0][:-3] if new_date else date

        date = date.strip(" *")
        dt = " ".join([year, date, meeting_time])
        dt = datetime.strptime(dt, "%Y %B %d %I:%M%p")

        return dt

    def _parse_title(self, date, meeting_type):
        if (date.startswith("**") or date.endswith("**")) and not (
            date.startswith("***") or date.endswith("***")
        ):
            return "Special " + meeting_type
        else:
            return meeting_type

    def _validate_location(self, response):
        loc = response.xpath("//strong")[-1].xpath(".//text()").extract()
        loc = [x.strip("\n ") for x in loc]
        loc = " ".join(loc[-2:])
        if "3600" not in loc:
            raise ValueError("Meeting location has changed")
