from datetime import datetime

import scrapy
import re
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookJusticeAdvisorySpider(CityScrapersSpider):
    name = "cook_justice_advisory"
    agency = "Cook County Justice Advisory"
    timezone = "America/Chicago"
    allowed_domains = ["www.cookcountyil.gov"]

    def start_requests(self):
        # old stuff:
        # url = "https://www.cookcountyil.gov/service/justice-advisory-council-meetings"
        # yield scrapy.Request(url=url, method="GET", callback=self.parse)

        today = datetime.now()
        for month_delta in range(-3, 0):
            mo_str = (today + relativedelta(months=month_delta)).strftime("%Y-%m")
            url = 'https://www.cookcountyil.gov/calendar-node-field-date/month/{}'.format(mo_str)
            # print(url)
            yield scrapy.Request(url=url, method='GET', callback=self.parse)

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
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(response),
            classification=ADVISORY_COMMITTEE,
            start=self._parse_start(response),
            end=self._parse_end(response),
            time_notes="",
            all_day=self._parse_all_day(response),
            location=self._parse_location(response),
            # links=self._parse_links(response),
            source=response.url,
        )

        meeting["links"] = self._parse_links(meeting)

        meeting["id"] = self._get_id(meeting) # need a get_id and get_status method? these lines cause
        meeting["status"] = self._get_status(meeting)
        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all justice advisory council (JAC in calendar) meetings on the page
        """
        return [
            response.urljoin(href)
            for href in response.xpath('//a[contains(text(), "JAC")]|//a[contains(text(), "Justice Advisory")]')
            .css("a::attr(href)")
            .extract()
            
        ]

    def _parse_location(self, response):
        """
        Parse or generate location. Url, latitude and longitude are all
        optional and may e more trouble than they're worth to collect.
        """
        address = response.xpath(
            '//div[@class="field event-location"]/descendant::*/text()'
        ).extract()
        for word in ["Location:", ", ", " "]:
            address.remove(word)
        address = " ".join(address)
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
        # title = response.css("h1::text").extract()
        title = ''.join(response.css("h1::text").extract())
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

    def _parse_links(self, meeting):
        date = meeting['start']

        url = "https://www.cookcountyil.gov/service/justice-advisory-council-meetings"

        yield scrapy.Request(url=url, method='GET', callback=self._parse_agenda, meta={'meeting_date': date})


        # links = link_response.css("span.file a::attr(href)").extract()
        # files = response.css("span.file a")

        # dates = link_response.css("span.file a::attr(href)").re(r"((?:\d{1,2})(?:\.|_|-)(?:\d{1,2})(?:\.|_|-)(?:\d{2,4}))")
        # ((?:\d{1,2})(?:\.|_|-)(?:\d{1,2})(?:\.|_|-)(?:\d{2,4})) some regex fun :)

        # return [
        #     {
        #         "href": f.xpath("./@href").extract_first(),
        #         "title": f.xpath("./text()").extract_first(),
        #     }
        #     for f in files
        # ]
       
        # date = meeting['start'].strftime("%m/%d/%Y")

    def _parse_agenda(self, response):
        files = response.css("span.file a").extract()
        meeting_date = response.meta.get('meeting_date')

        for f in files:
            link = f.xpath("./@href").extract_first()
            title = f.xpath("./text()").extract_first()
            date = datetime.strftime(link.re(r"((?:\d{1,2})(?:\.|_|-)(?:\d{1,2})(?:\.|_|-)(?:\d{2,4}))")) 

            if (date == meeting_date.date()):
                return [{ "href": link, "title": title, }]
        return []

