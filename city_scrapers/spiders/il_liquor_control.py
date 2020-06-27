import datetime
import re

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlLiquorControlSpider(CityScrapersSpider):
    name = "il_liquor_control"
    agency = "Illinois Liquor Control Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://www2.illinois.gov/ilcc/Divisions/Pages/Legal/"
        "Hearing-Schedule-for-Chicago-IL-and-Springfield-IL.aspx",
        "https://www2.illinois.gov/ilcc/Divisions/Pages/Legal/Meeting-minutes.aspx",
    ]  # start_urls[0] contains links future meetings. start_urls[1] contains past
    # meeting minutes links
    custom_settings = {"HTTPERROR_ALLOW_ALL": True}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        Each tentative meeting has own page. start_urls[0] is only used to get links
        for the pages.
        The links are sent to _next_meeting.
        start_urls[1] is for obtaining datetime info for past meetings.
        Then attempt to parse details page. If not status == 200, parses generic Meeting
        object with meeting date info.
        """

        if response.url == self.start_urls[0]:
            for future_meeting_href in response.css(
                "div.soi-link-item a::attr(href)"
            ).extract():
                yield response.follow(future_meeting_href, callback=self._next_meeting)

        if response.url == self.start_urls[1]:
            for past_meeting in response.css("div.link-item a"):
                past_meeting_text = past_meeting.css("*::text").extract_first()
                past_meeting_date_str = re.sub(
                    r"[Mm]inute.*", "", past_meeting_text
                ).strip()
                minutes_href = past_meeting.attrib["href"]
                dt_object = datetime.datetime.strptime(
                    past_meeting_date_str, "%B %d, %Y"
                )
                meeting_url = (
                    "https://www2.illinois.gov/ilcc/Events/Pages/Board-"
                    "Meeting-{0}-{1}-{2:%y}.aspx".format(
                        dt_object.month, dt_object.day, dt_object
                    )
                )
                if datetime.datetime.now() - dt_object < datetime.timedelta(days=365):
                    yield response.follow(
                        meeting_url,
                        callback=self._prev_meeting,
                        cb_kwargs=dict(minutes_href=minutes_href, dt_object=dt_object),
                    )

    def _next_meeting(self, response):
        dt_str = " ".join(
            [x.strip() for x in response.css("div.soi-event-data::text").extract()]
        )  # Extract string that contains datetime info.
        meeting = Meeting(
            title=self._parse_title(response),
            description="",
            classification=BOARD,
            start=self._parse_start(dt_str),
            end=self._parse_end(dt_str),
            all_day=False,
            time_notes="",
            location=self._parse_location(response),
            links=self._parse_link(response, self._parse_start(dt_str), None),
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _prev_meeting(self, response, **kwargs):
        minutes_href = kwargs["minutes_href"]
        dt_object = kwargs["dt_object"]
        if response.status == 200:
            dt_str = " ".join(
                [x.strip() for x in response.css("div.soi-event-data::text").extract()]
            )
            meeting = Meeting(
                title=self._parse_title(response),
                description="",
                classification=BOARD,
                start=self._parse_start(dt_str),
                end=self._parse_end(dt_str),
                all_day=False,
                time_notes="",
                location=self._parse_location(response),
                links=self._parse_link(
                    response, self._parse_start(dt_str), minutes_href
                ),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        else:
            meeting = Meeting(
                title="Board Meeting",
                description="",
                classification=BOARD,
                start=dt_object + datetime.timedelta(hours=13),
                end=dt_object + datetime.timedelta(hours=16),
                all_day=False,
                time_notes="Meeting time is estimated.",
                location={"address": "100 West Randolph 9-040 Chicago, IL", "name": ""},
                links=self._parse_link(response, dt_object, minutes_href),
                source=minutes_href,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return response.css("p.soi-eventType::text").extract_first().strip()

    def _parse_start(self, dt_str):
        """Parse start datetime as a naive datetime object."""

        return datetime.datetime.strptime(
            " ".join(dt_str.split()[:6]), "%A, %B %d, %Y %I:%M %p"
        )

    def _parse_end(self, dt_str):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return datetime.datetime.strptime(
            " ".join(dt_str.split()[:4] + dt_str.split()[7:]), "%A, %B %d, %Y %I:%M %p"
        )

    def _parse_location(self, response):
        """Parse or generate location."""
        loc_str = " ".join(
            [
                x.strip()
                for x in response.css("div.soi-eventlocation div::text").extract()
            ]
        )
        return {
            "address": "{} Chicago, IL".format(" ".join(loc_str.split()[:4])),
            "name": "",
        }

    def _parse_link(self, response, dt_object, minutes_href):
        """Use agenda_href if it is found from detail page. If not, try href using formatting
        datetime. """
        links = []
        agenda_href = response.css("div.item.link-item.bullet a::attr(href)").extract()
        if agenda_href:
            links.append({"title": "Agenda", "href": agenda_href[0]})
        if minutes_href:
            links.append({"title": "Minutes", "href": minutes_href})
        return links
