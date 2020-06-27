import json
import re
from datetime import datetime
from io import BytesIO

import scrapy
from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from PyPDF2 import PdfFileReader


class IlPollutionControlSpider(CityScrapersSpider):
    name = "il_pollution_control"
    agency = "Illinois Pollution Control Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://pcb.illinois.gov/ClerksOffice/MeetingMinutes",
        "https://pcb.illinois.gov/CurrentAgendas",
    ]
    json_url = "https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents"
    calendar_url = "https://pcb.illinois.gov/ClerksOffice/Calendar"

    def __init__(self, *args, **kwargs):
        self.minutes_map = dict()  # Populated by self._parse_minutes()
        self.agenda_map = dict()  # Populated by self._parse_agenda()
        self.relevant_years = [
            str(y) for y in range(datetime.now().year - 1, datetime.now().year + 1)
        ]
        super().__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """ Overridden `from_crawler` to connect `spider_idle` signal. """
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def spider_idle(self):
        """
        React to `spider_idle` signal by starting JSON parsing after _parse_minutes.
        """
        self.crawler.signals.disconnect(
            self.spider_idle, signal=scrapy.signals.spider_idle
        )
        self.crawler.engine.crawl(
            scrapy.Request(self.json_url, callback=self._parse_json), self
        )
        raise scrapy.exceptions.DontCloseSpider

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        # Gather and store links to meeting minutes:
        for item in response.xpath("//iframe/@src"):
            yield scrapy.Request(item.get(), callback=self._parse_minutes)

        # Gather and store link to agenda:
        for agenda_url in self._parse_agenda_page(response):
            yield scrapy.Request(agenda_url, callback=self._parse_agenda)

    def _parse_minutes(self, response):
        """ Traverse tree of URLs and populate self.minutes_map """
        for item in response.xpath("//td[@class='name']/a"):
            try:
                href = item.xpath("@href")[0].get()
                text = item.xpath("b/text()")[0].get().strip()
                if not any([(year in text) for year in self.relevant_years]):
                    continue  # Link does not contain documents from recent years
                if text[-4:] == ".pdf":
                    text = text[:-4]
            except IndexError:
                continue

            url = response.urljoin(href)
            if ".pdf" not in url:
                # Not a link to meeting minutes file - go a level deeper
                yield scrapy.Request(url, callback=self._parse_minutes)
            else:
                # Dates are given in several formats:
                format_strs = ["%m-%d-%Y", "%m-%d-%y", "%m/%d/%Y", "%m/%d/%y"]
                dt = None
                for format_str in format_strs:
                    try:
                        dt = datetime.strptime(text, format_str).date()
                    except ValueError:
                        continue
                    else:
                        break  # Found a format_str that matches - stop looking
                if dt is None:
                    continue  # Could not find matching format_str - can't process link.

                self.minutes_map[dt] = url

    def _parse_agenda_page(self, response):
        """Scrape link to agenda PDF"""
        for item in response.xpath("//div/div/a"):
            for _ in item.xpath(".//div/h5[text()='Board Meeting']"):
                for href in item.xpath("./@href"):
                    yield href.get()

    def _parse_agenda(self, response):
        """Parse PDF with agenda for date and store link + date"""
        pdf_obj = PdfFileReader(BytesIO(response.body))
        pdf_text = pdf_obj.getPage(0).extractText().replace("\n", "")

        # Find and extract strings for month/day/year:
        regex = re.compile(r"(?P<month>[a-zA-Z]+) (?P<day>[0-9]+), (?P<year>[0-9]{4})")
        m = regex.search(pdf_text)

        try:
            month = datetime.strptime(m.group("month"), "%B").month
            day = int(m.group("day"))
            year = int(m.group("year"))
            self.agenda_map[datetime(year, month, day).date()] = response.url
        except AttributeError:  # Regex failed to match.
            return None

        return None

    def _parse_json(self, response):
        """
        Parse JSON from /ClerksOffice/GetCalendarEvents -> Meetings
        """
        data = json.loads(response.body_as_unicode())

        for item in data:
            if any(
                s in item["CalendarTypeDesc"].lower()
                for s in ("holiday", "seminar", "hearing")
            ):
                continue  # Not interested in this event type

            title = item["CalendarTypeDesc"].replace("CANCELLED", "").strip()
            meeting = Meeting(
                title=title,
                description="",  # Too inconsistent to parse accurately
                classification=self._parse_classification(title),
                start=self._parse_start(item),
                end=None,
                all_day=item["IsFullDay"],
                time_notes="",
                location=self._parse_location(item),
                links=list(),
                source=self._parse_source(item, response),
            )

            meeting["links"] = self._parse_links(meeting)
            meeting["status"] = self._get_status(
                meeting,
                text=" ".join([item["CalendarTypeDesc"], item["Description"]]).lower(),
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "Board" in title:
            return BOARD
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        return datetime.strptime(item["StartDateTime"], "%m/%d/%Y %I:%M:%S %p")

    def _parse_location(self, item):
        """Parse or generate location."""
        text = " ".join([item["Description"], item["Location"]]).lower()
        if "thompson" in text:
            return {
                "address": "James R. Thompson Center - 100 W. Randolph St. Suite 11-500, Chicago, IL 60601",  # noqa
                "name": "Chicago IPCB Office",
            }
        elif "springfield" in text or "llinois pollution control board" in text:
            return {
                "address": "1021 N. Grand Ave. E. - Room 1244 N, Springfield, IL 62702",
                "name": "Springfield IPCB Office",
            }
        elif "sangamo room" in text:
            return {
                "address": "1021 N. Grand Ave. E. - Sangamo Room, Springfield, IL 62702",  # noqa
                "name": "Illinois EPA",
            }
        else:
            return {
                "address": "",
                "name": "",
            }

    def _parse_links(self, meeting):
        """ Associate Meeting objects with previously-scraped links """
        links = list()
        key = meeting["start"].date()
        if key in self.minutes_map:
            links.append({"href": self.minutes_map[key], "title": "Minutes"})
        if key in self.agenda_map:
            links.append({"href": self.agenda_map[key], "title": "Agenda"})

        return links

    def _parse_source(self, item, response):
        """Parse or generate source."""
        rel_url = scrapy.Selector(text=item["Description"]).xpath(".//a/@href").get()
        if rel_url:
            return response.urljoin(rel_url)
        else:
            return self.calendar_url
