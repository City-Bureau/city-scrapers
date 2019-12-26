from datetime import datetime
from scrapy.utils.log import configure_logging
import logging
import json
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
    # TODO remove before merging
    configure_logging(install_root_handler=False)
    logging.basicConfig(
            filename='log.txt',
            format='%(levelname)s: %(message)s',
            level=logging.DEBUG
    )

    def parse(self, response):
        """
        For some reason when we go to the start_url only the first five
        meetings are displayed. If you click the "Next Events" link from
        the first page, a few events actually get skipped, events that
        would have fallen after the last event on page 1 and before the
        first event on page 2. It seems like those events are supposed
        to be rendered on page 1 but they just aren't for some reason.

        If you hit "Next Events" and then hit "Previous Events" to go back,
        it seems to render those missing events. So in parse we click
        "Next Events", then in _setup we click "Previous Events", then in
        _parse_meetings we should theoretically be at the complete first page.
        
        If this problem with the website gets fixed, in theory this ritual
        won't be necessary but it won't break the crawler either.
        """
        next_page = response.css(
            "#tribe-events-footer .tribe-events-nav-pagination "
            ".tribe-events-sub-nav .tribe-events-nav-next a::attr(href)"
        ).extract_first()
        frmdata = {
            "action": "tribe_list",
            "tribe_paged" : "1",
            "tribe_event_display": "list",
            "featured" : "false",
            "tribe_event_category" : "board-meeting",
            "tribe-bar-date": "2018-01-01"
        }
        yield scrapy.FormRequest("https://95thstreetba.org/wp-admin/admin-ajax.php", method="POST", callback=self._parse_meetings, meta={"tribe_paged": 1}, formdata=frmdata)

    def _parse_meetings(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # raise ValueError(response.body)
        body = response.body.decode("utf-8")
        body = json.loads(body)
        rsel = scrapy.Selector(text=body['html'])
        obj = rsel.css(".tribe-events-loop .tribe-events-category-board-meeting")
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
            trpage = str(int(response.meta.get("tribe_paged"))+1)
            frmdata = {
                "action": "tribe_list",
                "tribe_paged" : trpage,
                "tribe_event_display": "list",
                "featured" : "false",
                "tribe_event_category" : "board-meeting",
                "tribe-bar-date": "2018-01-01"
            }
            yield scrapy.FormRequest(next_page, callback=self._parse_meetings, method="POST", meta={"tribe_paged": trpage}, formdata=frmdata)

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
            dayof = dayof.replace(year=datetime.today().year)
        #    raise ValueError(dayof);
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
