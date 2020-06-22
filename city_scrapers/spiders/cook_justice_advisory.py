import re
from collections import defaultdict
from datetime import datetime

import scrapy
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookJusticeAdvisorySpider(CityScrapersSpider):
    name = "cook_justice_advisory"
    agency = "Cook County Justice Advisory"
    timezone = "America/Chicago"
    allowed_domains = ["www.cookcountyil.gov"]
    
    def __init__(self, agenda_map=None):
        self.agenda_map = defaultdict(list)
        
    def start_requests(self):
        url = "https://www.cookcountyil.gov/service/justice-advisory-council-meetings"
        yield scrapy.Request(
            url=url, callback=self._parse_links, dont_filter=True,
        )
        today = datetime.now()
        for month_delta in range(-3, 6):
            mo_str = (today + relativedelta(months=month_delta)).strftime("%Y-%m")
            url = (
                "https://www.cookcountyil.gov/"
                "calendar-node-field-date/month/{}".format(mo_str)
            )
            yield scrapy.Request(url=url, method="GET", callback=self.parse)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

    def _parse_event(self, response):
        """Parse the event page."""
        agenda_map = self.agenda_map
        title = self._parse_title(response)
        start = self._parse_start(response)
        meeting_year = int(start.strftime("%y"))
        meeting_month = int(start.strftime("%m"))

        meeting = Meeting(
            title=title,
            description=self._parse_description(response),
            classification=ADVISORY_COMMITTEE,
            start=start,
            end=self._parse_end(response),
            time_notes="",
            all_day=self._parse_all_day(response),
            location=self._parse_location(response),
            links=agenda_map[str(meeting_year) + "-" + str(meeting_month)],
            source=response.url,
        )

        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)

        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all justice advisory council (JAC in calendar) meetings on the page
        """
        return [
            response.urljoin(href)
            for href in response.xpath(
                '//a[contains(text(), "JAC")]|//a[contains(text(), "Justice Advisory")]'
            )
            .css("a::attr(href)")
            .extract()
        ]

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        address = response.xpath(
            '//div[@class="field event-location"]/descendant::*/text()'
        ).extract()
        for word in ["Location:", ", ", " "]:
            address.remove(word)
        address = " ".join(address)
        if "Microsoft Teams" in address:
            return {
                "address": "",
                "name": "",
            }
        else:
            return {
                "address": address,
                "name": "",
            }

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        date = "".join(date).upper()
        return "ALL DAY" in date

    def _parse_title(self, response):
        """Parse or generate event"""
        title = "".join(response.css("h1::text").extract())
        if "JAC Council Meeting" in title:
            return "JAC Council Meeting"
        else:
            return title

    def _parse_description(self, response):
        """Parse or generate event description."""
        category_field = response.xpath(
            "//div[contains(., 'Category:') and contains(@class, 'field-label')]"
        )
        field_items = category_field.xpath(
            "./following::div[contains(@class, 'field-items')]"
        )
        return " ".join(
            field_items.xpath(".//p/text()").extract()
            + field_items.xpath(".//strong/text()").extract()
        ).strip()

    def _parse_start(self, response):
        """Parse start date and time"""
        start = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        start = "".join(start).upper()
        start = start.split(" TO ")[0].strip()
        start = start.replace("(ALL DAY)", "12:00AM")

        return datetime.strptime(start, "%B %d, %Y %I:%M%p")

    def _parse_end(self, response):
        """Parse end date and time"""
        date = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        date = "".join(date).upper()
        date.replace("(ALL DAY)", "TO 11:59PM")
        start_end = date.split(" TO ")

        if len(start_end) < 2:
            return

        end_time = start_end[1]
        date = start_end[0][: start_end[0].rindex(" ")]
        return datetime.strptime("{} {}".format(date, end_time), "%B %d, %Y %I:%M%p")

    def _parse_links(self, response):
        """Parse links"""
        agenda_map = self.agenda_map

        links = response.css('span.file a')
        links = links[2:]
        for index, link in enumerate(links):
            link_name = link.xpath('text()').extract_first()
            link_name = link_name.replace('\xa0', ' ')
            link_path = link.xpath('./@href').extract_first()
            

        """
        files = response.css("span.file a")
        files = files[2:]
        for f in files:
            link = f.xpath("./@href").extract_first()

            pattern = r"(?P<m>\d{1,2})(?:\.|_|-)(?:\d{1,2})(?:\.|_|-)(?P<y>\d{2,4})"
            regex = re.search(pattern, link)

            if regex is not None:
                y = int(regex.group("y")) % 2000
                m = int(regex.group("m"))
                agenda_map[str(y) + "-" + str(m)] = [{"href": link, "title": "Agenda"}]
        """
