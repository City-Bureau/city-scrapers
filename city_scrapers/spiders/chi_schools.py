import re
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSchoolsSpider(CityScrapersSpider):
    name = "chi_schools"
    agency = "Chicago Public Schools"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.cpsboe.org/meetings/past-meetings",
        "https://www.cpsboe.org/meetings",
    ]
    location = {
        "name": "CPS Loop Office, Board Room",
        "address": "42 W Madison St, Chicago, IL 60602",
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Connect to spider_idle for when all detail pages are scraped"""
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.meeting_dates = []
        crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def spider_idle(self):
        """Parse planning calendar after all detail pages scraped"""
        self.crawler.signals.disconnect(
            self.spider_idle, signal=scrapy.signals.spider_idle
        )
        self.crawler.engine.crawl(
            scrapy.Request(
                "https://www.cpsboe.org/meetings/planning-calendar",
                callback=self._parse_calendar,
            ),
            self,
        )
        raise scrapy.exceptions.DontCloseSpider

    def parse(self, response):
        if "past" in response.url:
            # Only pull past 2 years of meetings
            for link in response.css(".past-meetings")[:2].css("th a"):
                yield response.follow(link.attrib["href"], callback=self._parse_detail)
        else:
            for link in response.css(".meetings dl a:not(.action)"):
                yield response.follow(link.attrib["href"], callback=self._parse_detail)

    def _parse_detail(self, response):
        """Parse information from meeting detail pages"""
        title = self._parse_title(response)
        start = self._parse_start(
            re.sub(r"\s+", " ", " ".join(response.css("h2.datetime *::text").extract()))
        )
        if not start:
            return
        self.meeting_dates.append(start.date())
        meeting = Meeting(
            title=title,
            description=self._parse_description(response),
            classification=self._parse_classification(title),
            start=start,
            end=None,
            time_notes="",
            all_day=False,
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting["status"] = self._parse_status(meeting, meeting["description"])
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_calendar(self, response):
        for item in response.css("#content-primary tr"):
            start = self._parse_start(
                re.sub(
                    r"\s+", " ", " ".join(item.css("td:first-child *::text").extract())
                )
            )
            if not start or start.date() in self.meeting_dates:
                continue
            meeting = Meeting(
                title="Board of Education",
                description="",
                classification=BOARD,
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(response),
                links=[],
                source=response.url,
            )
            meeting["status"] = self._parse_status(
                meeting, re.sub(r"\s+", " ", " ".join(item.css("*::text").extract()))
            )
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, response):
        title_str = " ".join(
            response.css("#content-primary h1::text").extract()
        ).strip()
        if "Special" in title_str:
            return title_str
        if "Board" in title_str:
            return "Board of Education"
        return title_str.replace("Meeting", "").strip()

    def _parse_description(self, response):
        split_lines = (
            response.css("#content-primary > *:not(table):not(.box)")[3:-1]
            .css("*::text")
            .extract()
        )
        combined_lines = " ".join(
            [
                re.sub(r"\s+(?=\n)", "", re.sub(r"[^\S\n]+", " ", line))
                for line in split_lines
            ]
        )
        cleaned_text = "\n".join(
            [line.strip() for line in combined_lines.split("\n")]
        ).strip()
        return re.sub(r"((?<=\n\n)\n+|(?<=[^\S\n])\s| (?=[\.,]))", "", cleaned_text)

    def _parse_status(self, meeting, description):
        reschedule_date_match = re.search(
            r"((?<=rescheduled to )|(?<=held on ))([a-z]{6}day,? )?[a-z]{3,10} [0-9]{1,2}([a-z]{2})?,? \d{4}",  # noqa
            description,
            flags=re.I,
        )
        # If text mentions a rescheduled date, check if it's the assigned meeting date
        if reschedule_date_match:
            reschedule_date_str = reschedule_date_match.group()
            date_str = re.sub(
                r"((?<=\d)[a-z]{2}|,)",
                "",
                re.search(
                    r"[A-Z][a-z]{2,9} [0-9]{1,2}([a-z]{2})?,? \d{4}",
                    reschedule_date_str,
                ).group(),
            )
            date_obj = datetime.strptime(date_str, "%B %d %Y").date()
            # If the parsed meeting date is the same as rescheduled,
            # ignore description in cancellation
            if meeting["start"].date() == date_obj:
                return self._get_status({**meeting, "description": ""})
        return self._get_status(meeting, text=description)

    def _parse_classification(self, title):
        if "Committee" in title:
            return COMMITTEE
        if "hearing" in title.lower():
            return FORUM
        return BOARD

    def _parse_start(self, dt_str):
        date_match = re.search(r"[A-Z][a-z]{2,8} \d{1,2},? \d{4}", dt_str)
        if not date_match:
            return
        date_str = date_match.group().replace(",", "")
        time_match = re.search(r"(\d{1,2}(:\d{2})? ?[apmAPM\.]{2,4})", dt_str)
        time_str = "12:00am"
        if time_match:
            time_str = re.sub(r"[\s\.]", "", time_match.group())
        dt_fmt = "%B %d %Y %I:%M%p"
        if ":" not in time_str:
            dt_fmt = "%B %d %Y %I%p"
        return datetime.strptime(" ".join([date_str, time_str]), dt_fmt)

    def _parse_location(self, response):
        addr_input = " ".join(response.css("#mapAddress::attr(value)").extract())
        loc_lines = response.css("h2.datetime + p")[:1].css("*::text").extract()
        if len(loc_lines) == 0:
            loc_lines = response.css("td:last-child *::text").extract()
        if addr_input:
            addr_split = [p.strip() for p in addr_input.split("|") if p.strip()]
            loc_name = ""
            if len(addr_split) > 2:
                loc_name = addr_split[0]
                loc_addr = " ".join(addr_split[1:])
            else:
                loc_addr = " ".join(addr_split)
            if "42 W" in loc_addr:
                return self.location
            return {
                "name": loc_name,
                "address": loc_addr,
            }
        elif len(loc_lines) > 0:
            loc_list = [line.strip() for line in loc_lines if "calendar" not in line]
            loc_name = ""
            loc_addr = ""
            # If the first char of the location str is a number, assume it's the address
            if loc_list[0][0].isdigit():
                loc_addr = " ".join(loc_list)
            else:
                loc_name = loc_list[0]
                loc_addr = " ".join(loc_list[1:])
            if "42 W" in loc_addr:
                return self.location
            return {
                "name": loc_name.strip(),
                "address": loc_addr.strip(),
            }
        return self.location

    def _parse_links(self, response):
        links = []
        for link in response.css("#content-primary a"):
            title = " ".join(link.css("*::text").extract()).strip()
            if (
                "calendar" in title.lower()
                or "back to meetings" in title.lower()
                or "past-meetings" in title.lower()
            ):
                continue
            links.append(
                {"title": title, "href": response.urljoin(link.attrib["href"])}
            )
        return links
