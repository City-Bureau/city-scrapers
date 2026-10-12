import re
from datetime import datetime

import scrapy
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    COMMITTEE,
    FORUM,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta
from w3lib.html import remove_tags

# .NET ticks (100ns intervals since 0001-01-01) at the Unix epoch. The calendar's
# `bd` parameter is a begin date expressed in ticks.
TICKS_AT_EPOCH = 621355968000000000


class IlCommerceSpider(CityScrapersSpider):
    name = "il_commerce"
    agency = "Illinois Commerce Commission"
    timezone = "America/Chicago"
    base_url = "https://www.icc.illinois.gov/meetings?scm=True&sps=True&sh=True&sjc=True&ssh=False&smceb=True"  # noqa
    # Month view (dts=32) of the calendar page
    start_urls = [base_url + "&dts=32"]
    default_location = {
        "name": "Illinois Commerce Commission",
        "address": "527 East Capitol Avenue, Springfield, IL 62701",
    }

    def start_requests(self):
        """
        Start from the month one year back and page forward one month at a time.
        With dts=32 and a `bd` begin date, the calendar shows the whole month that
        contains `bd`.
        """
        month = (datetime.now() - relativedelta(years=1)).replace(day=1)
        yield self._month_request(month)

    def _month_request(self, month):
        """Request the calendar month starting at `month`, with `bd` in ticks."""
        seconds = int((month - datetime(1970, 1, 1)).total_seconds())
        ticks = TICKS_AT_EPOCH + seconds * 10**7
        return scrapy.Request(
            "{}&bd={}&dts=32".format(self.base_url, ticks),
            callback=self.parse,
            cb_kwargs={"month": month},
        )

    def parse(self, response, month=None):
        """
        Follow each meeting link on a calendar month to its detail page, then
        request the next month. Paging stops at the first empty month after the
        current one, since meetings are only posted a few months ahead.
        """
        event_links = response.css(".p-2 a.day")
        for event_link in self._skip_replaced_listings(event_links):
            href = event_link.attrib["href"]
            yield response.follow(href, callback=self._parse_event_page)
        if month is None:
            return
        is_future = month > datetime.now()
        if not event_links and not is_future:
            self.logger.warning("No meetings found on %s", response.url)
        if event_links or not is_future:
            yield self._month_request(month + relativedelta(months=1))

    def _skip_replaced_listings(self, event_links):
        """
        When the ICC re-posts a meeting, the old listing stays on the calendar
        marked "Cancelled" next to the new one, with the same title and time. Both
        would get the same id, so drop the cancelled listing when an active one
        exists for the same title and time.
        """
        cards = []
        for event_link in event_links:
            title = re.sub(r"\s+", " ", " ".join(event_link.css("*::text").extract()))
            when = re.sub(
                r"\s+", " ", " ".join(event_link.xpath("../h3/text()").extract())
            )
            cancelled = (
                "cancel"
                in " ".join(event_link.xpath("../h3//span//text()").extract()).lower()
            )
            cards.append((event_link, (title.strip(), when.strip()), cancelled))
        active = {key for _, key, cancelled in cards if not cancelled}
        for event_link, key, cancelled in cards:
            if cancelled and key in active:
                self.logger.info(
                    "Skipping %s, replaced by an active listing",
                    event_link.attrib["href"],
                )
                continue
            yield event_link

    def _parse_event_page(self, response):
        panel = response.css(".soi-icc-container > .row > .col-12")
        start = self._parse_start(panel)
        if start is None:
            self.logger.warning("Could not parse start time from %s", response.url)
            return
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(panel),
            classification=self._parse_classification(title),
            start=start,
            end=None,
            all_day=False,
            time_notes="",
            location=self._parse_location(panel),
            links=self._parse_links(panel, response),
            source=response.url,
        )
        status_str = " ".join(response.css("h3 *::text").extract())
        meeting["status"] = self._get_status(meeting, text=status_str)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, selector):
        """
        Parse or generate meeting title. The h2 holds the body's name followed by a
        span with the meeting name. For the Commission itself, use the meeting name
        (e.g. "Regular Open Meeting"). For other bodies, use the body's name, since
        the span only repeats it (e.g. "Motor Carrier Employee Board Meeting"). Some
        policy sessions add a second span repeating the name with the date, so only
        the first span is used.
        """
        body_str = " ".join(selector.css(".soi-container h2::text").extract()).strip()
        meeting_str = " ".join(
            selector.css(".soi-container h2 span")[:1].css("*::text").extract()
        ).strip()
        body_str = re.sub(r"\s+", " ", body_str)
        meeting_str = re.sub(r"\s+", " ", meeting_str)
        if body_str and body_str != self.agency:
            return body_str
        return meeting_str

    def _parse_description(self, selector):
        """Parse or generate meeting description."""
        return re.sub(
            r"\s+", " ", " ".join(selector.css(".mt-4+ p *::text").extract())
        ).strip()

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "public forum" in title.lower():
            return FORUM
        if "advisory" in title.lower():
            return ADVISORY_COMMITTEE
        if "committee" in title.lower():
            return COMMITTEE
        if "board" in title.lower():
            return BOARD
        return COMMISSION

    def _parse_start(self, selector):
        """
        Parse start datetime as a naive datetime object. The page shows the date as
        "October 15, 2026 at 11:30 AM", and the time used to sit in a separate span
        without the "at", so the word is optional. Returns None if no date is found.
        """
        start_str = re.sub(
            r"\s+", " ", " ".join(selector.css("h3.mt-4 *::text").extract())
        )
        match = re.search(
            r"([A-Z][a-z]{2,8} \d{1,2}, \d{4}) (?:at )?(\d{1,2}:\d{2} [AP]M)",
            start_str,
        )
        if not match:
            return None
        return datetime.strptime(" ".join(match.groups()), "%B %d, %Y %I:%M %p")

    def _parse_location(self, selector):
        """
        Parse location. A full location starts with the street and ends with the
        city, which make up the address, and the lines between them are the name.
        The state is written as "IL" to match the default location, since some pages
        spell out "Illinois".
        That is usually three lines, but some Chicago hearings split building,
        floor and room into separate lines. A Webex meeting lists Webex as the middle
        line but is held online, so its address is left empty. Pages that only say
        "Illinois Commerce Commission", or show no location at all, are checked for
        a venue in the description, and otherwise get the Commission's Springfield
        office. Other one-line locations, such as a video conference, keep that line
        as the name.
        """
        location_block = selector.css(".row.mt-4 > .col-12")
        if len(location_block) == 0:
            return self._parse_description_location(selector)
        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in location_block[0].css("p *::text").extract()
        ]
        lines = [line for line in lines if line]
        if len(lines) >= 3:
            name = ", ".join(lines[1:-1])
            if "webex" in name.lower():
                return {"name": name, "address": ""}
            city = re.sub(r",\s*Illinois\s+(?=\d{5})", ", IL ", lines[-1])
            return {
                "name": name,
                "address": "{}, {}".format(lines[0], city),
            }
        name = re.sub(
            r"\s+", " ", " ".join(location_block[0].css("h4 *::text").extract())
        ).strip()
        if lines:
            self.logger.warning("Unexpected location format: %s", lines)
            return {"name": name, "address": ", ".join(lines)}
        if not name or name == self.agency:
            return self._parse_description_location(selector)
        return {"name": name, "address": ""}

    def _parse_description_location(self, selector):
        """
        Public forums are held away from the ICC offices, and their pages only say
        "Illinois Commerce Commission" in the location box. The venue is the last
        paragraph of the description instead: the venue name, the street, any room,
        then the city, one per line. A forum held as a webinar says it takes place
        via WebEx, so it gets the same empty address as other Webex meetings. Any
        other page gets the Commission's Springfield office.
        """
        description = selector.css(".mt-4+ p").get() or ""
        last_paragraph = re.split(r"<br>\s*<br>", description)[-1]
        lines = [
            re.sub(r"\s+", " ", remove_tags(line)).strip()
            for line in re.split(r"<br>", last_paragraph)
        ]
        lines = [line for line in lines if line]
        if len(lines) >= 3 and re.search(r", (IL|Illinois)\b[\s\d]*$", lines[-1]):
            city = re.sub(r",\s*Illinois\b", ", IL", lines[-1])
            return {
                "name": ", ".join([lines[0]] + lines[2:-1]),
                "address": "{}, {}".format(lines[1], city),
            }
        if re.search(r"\bwebex\b", remove_tags(description), flags=re.I):
            return {"name": "Webex", "address": ""}
        return self.default_location

    def _parse_links(self, selector, response):
        """Parse or generate links."""
        links = selector.css(".row.mt-4 .list-unstyled a")
        urls = []
        if not links:
            return urls
        for link in links:
            urls.append(
                {
                    "title": " ".join(link.css("*::text").extract()).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return urls
