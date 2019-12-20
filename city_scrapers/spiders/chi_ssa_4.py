from datetime import datetime

import scrapy
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa4Spider(CityScrapersSpider):
    name = "chi_ssa_4"
    agency = "Chicago Special Service Area #4 South Western Avenue"
    timezone = "America/Chicago"
    start_urls = [
        "https://95thstreetba.org/events/category/board-meeting/?"
        "tribe_paged=1&tribe_event_display=list&tribe-bar-date=2017-10-01"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        obj = response.css(".tribe-events-loop .tribe-events-category-board-meeting")
        for item in obj:
            # Only grab things of class tribe-events-category-board-meeting
            start, end = self._parse_time(item)
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=start,
                end=end,
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        next_page = response.css(
            "#tribe-events-footer .tribe-events-nav-pagination "
            ".tribe-events-sub-nav .tribe-events-nav-next a::attr(href)"
        ).extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item.css(".tribe-events-list-event-title a::text").extract_first().strip()
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        desc = item.css(".tribe-events-list-event-description p::text").extract_first()
        return desc

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_time(self, item):
        """Parse start and end datetime as native datetime objects."""
        dtstart = item.css(
            ".tribe-events-event-meta .location .tribe-event-schedule-details"
            " .tribe-event-date-start::text"
        ).extract_first()
        tend = item.css(
            ".tribe-events-event-meta .location .tribe-event-schedule-details"
            " .tribe-event-time::text"
        ).extract_first()
        dtstart = dtstart.split("@")
        try:
            dayof = datetime.strptime(dtstart[0].strip(), "%B %d, %Y").date()
        except ValueError:
            # If year is omitted then they mean the current year
            dayof = datetime.strptime(dtstart[0].strip(), "%B %d").date()
            dayof.replace(year=datetime.today().year)
        start_time = datetime.strptime(dtstart[1].strip(), "%H:%M %p").time()
        end_time = datetime.strptime(tend.strip(), "%H:%M %p").time()

        start = datetime.combine(dayof, start_time)
        end = datetime.combine(dayof, end_time)
        return (start, end)

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        loc = dict()

        locbegin = ".tribe-events-event-meta .location .tribe-events-venue-details"
        loc["name"] = item.css(locbegin +
                               "::text").extract_first().split("<span")[0].strip(" \n\t,.")
        locaddr = locbegin + " .tribe-address"

        addr = ""
        addr += item.css(locaddr + " .tribe-street-address::text").extract_first().strip() + " "
        addr += item.css(locaddr + " .tribe-locality::text").extract_first().strip()
        addr += item.css(locaddr + " .tribe-delimiter::text").extract_first().strip() + " "
        addr += item.css(locaddr + " .tribe-region::text").extract_first().strip() + " "
        addr += item.css(locaddr + " .tribe-postal-code::text").extract_first().strip()
        loc["address"] = addr
        return loc

    def _parse_links(self, item):
        """Parse or generate links."""
        link = item.css(".tribe-events-list-event-description a::attr(href)").get()
        # title = item.css(".tribe-events-list-event-description a::text").extract_first()
        title = "meeting page"
        return [{"href": link, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.request.url
