from datetime import datetime

import requests
from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookPaceBoardSpider(CityScrapersSpider):
    name = "cook_pace_board"
    agency = "Pace Suburban Bus Services"
    timezone = "America/Chicago"
    start_urls = ["http://www.pacebus.com/sub/news_events/calendar_of_events.asp"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        # Address of Pace Headquarters. Where all meetings seem to be held
        hq_address = "550 W. Algonquin Rd., Arlington Heights, IL 60005"

        # Current year of meetings listed
        year = (
            response.xpath("//th[@class='rowheader']/em/strong/text()")
            .re(r"(\d\d\d\d) Meetings")[0]
            .strip()
        )

        # Get rows of meeting table
        meeting_rows = response.xpath(
            "//tr/td[@class='rowy2']/parent::* | \
            //tr/td[@class='rowl2']/parent::*"
        )

        for item in meeting_rows:
            meeting = Meeting(
                title=self._parse_title(item),
                description="",  # No description
                # classification -- do after based on title
                start=self._parse_start(item, year),
                end=None,  # No end time
                all_day=False,  # Probably not, usually starts in evening
                time_notes=None,
                location=self._parse_location(item, hq_address),
                # links -- do this after based on title and date,
                source=self.start_urls[0],
            )

            # Figure out classification from meeting title
            meeting["classification"] = self._parse_classification(
                title=meeting["title"]
            )

            # Figure out meeting documents from title and date
            meeting["links"] = self._parse_links(
                title=meeting["title"], date=meeting["start"]
            )

            meeting["status"] = self._get_status(
                meeting, text=" ".join(item.css("*::text").extract())
            )
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item.xpath("./td/strong/text()").get().strip()
        return title

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "board" in title.lower():
            return BOARD
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object."""
        date = item.xpath("./td[2]/text()").get().strip()
        time = item.xpath("./td[3]/text()").get().strip()
        if time == "N/A":
            time = "9:30am"
        # "January 16 2019 4:30pm"
        dt_string = "{date} {year} {time}".format(date=date, year=year, time=time)
        dt_format = "%B %d %Y %I:%M%p"
        start_datetime = datetime.strptime(dt_string, dt_format)
        return start_datetime

    def _parse_location(self, item, hq_address):
        """Parse or generate location."""
        location_name = " ".join(item.css("td")[-1].css("*::text").extract()).strip()

        # We know Pace Headquarters address, and it seems to be the only place
        # they hold these meetings
        if (
            "pace headquarters" in location_name.lower()
            or "cancel" in location_name.lower()
        ):
            location_address = hq_address
        else:
            raise ValueError(
                "Meeting not at location with known address. Please update spider."
            )

        return {
            "address": location_address,
            "name": location_name,
        }

    def _parse_links(self, title, date):
        """Parse or generate links."""
        out = []

        # We know how to guess the URL for board agenda and minutes
        if "board" in title.lower():

            # Agenda #
            # Looks like:
            # https://www.pacebus.com/pdf/Board_Minutes/
            # Pace_Board_Meeting_Agenda_February_13_2019.pdf
            agenda_base_url = "https://www.pacebus.com/pdf/Board_Minutes/"
            agenda_filename = "Pace_{title}_Agenda_{date}.pdf".format(
                title="Board_Meeting", date=date.strftime("%B_%d_%Y")
            )
            agenda_url = agenda_base_url + agenda_filename
            # Check whether there is a file there and append if so
            r_agenda = requests.get(agenda_url)
            if r_agenda.status_code == 200:
                out.append({"title": "Agenda", "href": agenda_url})

            # Minutes #
            # Looks like:
            # https://www.pacebus.com/pdf/Board_Minutes/
            # Pace_Board_Meeting_Minutes_Jan_2019.pdf
            minutes_base_url = "https://www.pacebus.com/pdf/Board_Minutes/"
            minutes_filename = "Pace_{title}_Minutes_{date}.pdf".format(
                title="Board_Meeting", date=date.strftime("%b_%Y")
            )
            minutes_url = minutes_base_url + minutes_filename
            # Check whether there is a file there and append if so
            r_minutes = requests.get(minutes_url)
            if r_minutes.status_code == 200:
                out.append({"title": "Minutes", "href": minutes_url})

        return out
