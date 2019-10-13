import json
from datetime import datetime
from urllib.parse import urljoin

import scrapy
from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlPollutionControlSpider(CityScrapersSpider):
    name = "il_pollution_control"
    agency = "Illinois Pollution Control Board"
    timezone = "America/Chicago"
    allowed_domains = ["pcb.illinois.gov"]
    start_urls = ["https://pcb.illinois.gov/ClerksOffice/MeetingMinutes"]
    json_url = "https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents"
    calendar_url = "https://pcb.illinois.gov/ClerksOffice/Calendar"

    def __init__(self, *args, **kwargs):
        self.link_map = dict()  # Populated by self._parse_minutes()
        self.relevant_years = [
            str(y) for y in range(datetime.now().year - 1,
                                  datetime.now().year + 1)
        ]
        super().__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """ Overridden `from_crawler` to connect `spider_idle` signal. """
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def spider_idle(self):
        """ React to `spider_idle` signal by starting JSON parsing after _parse_minutes."""
        self.crawler.signals.disconnect(self.spider_idle, signal=scrapy.signals.spider_idle)
        self.crawler.engine.crawl(scrapy.Request(self.json_url, callback=self._parse_json), self)
        raise scrapy.exceptions.DontCloseSpider

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        for item in response.xpath("//iframe/@src"):
            yield scrapy.Request(item.get(), callback=self._parse_minutes)

    def _parse_minutes(self, response):
        """ Traverse tree of URLs and populate self.link_map """
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

            url = urljoin("https://{}".format(self.allowed_domains[0]), href)
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
                    continue  # Could not find a matching format_str - can't process link.

                self.link_map[dt] = url

    def _parse_json(self, response):
        """ Parse JSON from https://pcb.illinois.gov/ClerksOffice/GetCalendarEvents -> Meetings """
        data = json.loads(response.body_as_unicode())

        for item in data:
            if any(
                s in item["CalendarTypeDesc"].lower() for s in ("holiday", "seminar", "hearing")
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
                source=self._parse_source(item),
            )

            meeting["links"] = self._parse_links(meeting)
            meeting["status"] = self._get_status(
                meeting, text=" ".join([item['CalendarTypeDesc'], item['Description']]).lower()
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
        return datetime.strptime(item["StartDateTime"], '%m/%d/%Y %I:%M:%S %p')

    def _parse_location(self, item):
        """Parse or generate location."""
        text = " ".join([item['Description'], item['Location']]).lower()
        if "thompson" in text:
            return {
                "address":
                    "James R. Thompson Center - 100 W. Randolph St. Suite 11-500, Chicago, IL 60601",  # noqa
                "name": "Chicago IPCB Office",
            }
        elif "springfield" in text or "llinois pollution control board" in text:
            return {
                "address": "1021 N. Grand Ave. E. - Room 1244 N, Springfield, IL 62702",
                "name": "Springfield IPCB Office",
            }
        elif "sangamo room" in text:
            return {
                "address": "1021 N. Grand Ave. E. - Sangamo Room, Springfield, IL 62702",
                "name": "Illinois EPA",
            }
        else:
            return {
                "address": "",
                "name": "",
            }

    def _parse_links(self, meeting):
        """ Associate Meeting objects with previously-scraped links """
        key = meeting['start'].date()
        if key in self.link_map:
            return [{"href": self.link_map[key], "title": "Minutes - {}".format(key)}]

    def _parse_source(self, item):
        """Parse or generate source."""
        rel_url = scrapy.Selector(text=item["Description"]).xpath(".//a/@href").get()
        if rel_url:
            return urljoin("https://{}".format(self.allowed_domains[0]), rel_url)
        else:
            return self.calendar_url
