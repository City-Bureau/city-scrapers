from datetime import datetime

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class ChiSsa4Spider(CityScrapersSpider):
    name = "chi_ssa_4"
    agency = "Chicago Special Service Area #4 South Western Avenue"
    timezone = "America/Chicago"

    def start_requests(self):
        today = datetime.now()
        for month_delta in range(-6, 3):
            mo_str = (today + relativedelta(months=month_delta)).strftime("%Y-%m")
            url = "http://95thstreetba.org/events/category/board-meeting/{}/".format(
                mo_str
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
        """Parse the event page"""
        meeting = Meeting(
            title=self._parse_title(response),
            description="",
            classification=COMMISSION,
            start=self._parse_start(response),
            end=self._parse_end(response),
            all_day=False,
            time_notes=self._parse_time_notes(response),
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        return meeting

    def _get_event_urls(self, response):
        """
        Get urls for all meetings on the calendar page
        """
        urls = []
        links = response.css(
            "table td.tribe-events-thismonth h3 a::attr(href)"
        ).extract()
        descriptions = response.css(
            "table td.tribe-events-thismonth h3 a::text"
        ).extract()

        for link, description in zip(links, descriptions):
            if "meeting" in description.lower():
                urls.append(link)
        return urls

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        title = "".join(response.css("div.tribe-events-single h1::text").get())
        return title.replace(" Meeting", "")

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        dt_start = response.css("abbr.dtstart::text").get()
        time_start = response.css("div.dtstart::text").get().split("-")
        try:
            date = datetime.strptime(dt_start.strip(), "%B %d, %Y")
        except ValueError:
            date = datetime.strptime(dt_start.strip(), "%B %d")
            date = date.replace(year=datetime.today().year)
        start = datetime.strptime(time_start[0].strip(), "%H:%M %p").time()
        return datetime.combine(date, start)

    def _parse_end(self, response):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        dt_start = response.css("abbr.dtstart::text").get()
        time_start = response.css("div.dtstart::text").get().split("-")
        try:
            date = datetime.strptime(dt_start.strip(), "%B %d, %Y")
        except ValueError:
            date = datetime.strptime(dt_start.strip(), "%B %d")
            date = date.replace(year=datetime.today().year)
        end = datetime.strptime(time_start[1].strip(), "%H:%M %p").time()
        return datetime.combine(date, end)

    def _parse_time_notes(self, response):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_location(self, response):
        """Parse or generate location."""
        name = response.css("dd.tribe-venue::text").get()
        street = response.css("span.tribe-street-address::text").get() + " "
        locality = response.css("span.tribe-locality::text").get() + ", "
        region = response.css("abbr.tribe-region::text").get() + " "
        postal_code = response.css("span.tribe-postal-code::text").get() + " "
        country = response.css("span.tribe-country-name::text").get()
        address = "".join([street, locality, region, postal_code, country])

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, response):
        """Parse or generate links."""
        links = response.css("div.tribe-events-content a::attr(href)").getall()
        links_text = response.css("div.tribe-events-content a::text").getall()
        files = []

        for link, text in zip(links, links_text):
            if "minutes" in text.lower():
                title = "Minutes"
            elif "agenda" in text.lower():
                title = "Agenda"
            else:
                title = text
            files.append({"href": link, "title": title})

        return files
