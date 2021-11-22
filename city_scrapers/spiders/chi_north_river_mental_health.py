import datetime

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthRiverMentalHealthSpider(CityScrapersSpider):
    name = "chi_north_river_mental_health"
    agency = (
        "North River Expanded Mental Health Services Program and Governing Commission"
    )
    timezone = "America/Chicago"
    main_url = "https://www.northriverexpandedmentalhealthservicescommission.org"
    start_urls = [
        f"{main_url}/minutes.html",
        f"{main_url}/index.html",
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        if response.url == self.start_urls[0]:
            yield from self._parse_minutes(response)

        else:
            yield from self._parse_index(response)

    def _parse_minutes(self, response):
        for item in response.xpath('.//div[@class="wsite-section-elements"]//a'):

            valid_start = self._minutes_parse_start(item)
            if not valid_start:
                continue

            meeting = Meeting(
                title="Governing Commission",
                description="",
                classification=COMMISSION,
                start=valid_start,
                end=None,
                all_day=False,
                time_notes="",
                location=self._minutes_parse_location(item),
                links=self._minutes_parse_links(item, response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_index(self, response):
        item = response.css("td:nth-child(2) div:nth-child(2)")
        meeting = Meeting(
            title="Governing Commission",
            description="",
            classification=COMMISSION,
            start=self._index_parse_start(item),
            end=None,
            all_day=False,
            time_notes="",
            location=self._index_parse_location(item),
            links=self._index_parse_links(item, response),
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _minutes_parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_components = item.re(
            "(?P<month>[A-Za-z\\.]+)\\ "
            "(?P<day>[0-9]+)(th)?,((\\ |\\xa0)?)"
            "(?P<year>[0-9]+)?"
        )

        try:
            if date_components[0] == "anuary":
                date_components[0] = "January"

            date_str = (
                f"{date_components[-1]} {date_components[0]} {date_components[1]}"
            )

            if date_str == "20 May 20":
                date_str = "20 May 2015"
            elif date_str == " September 21":
                date_str = "2016 September 21"
            elif date_str == "201 July 15":
                date_str = "2015 July 15"

            return dateutil.parser.parse(f"{date_str} 7PM")
        except IndexError:
            return None

    def _index_parse_start(self, item):
        date_components = item.re(
            "<br>Date: (?P<date>.*)<br>Time: (?P<time>.*)<br>Place:"
        )
        return dateutil.parser.parse(" ".join(date_components))

    def _minutes_parse_location(self, item):
        """Parse or generate location."""
        start = self._minutes_parse_start(item)
        if start < datetime.datetime(2017, 3, 15):
            return {
                "address": "3857 N. Kostner Avenue Chicago, IL 60641",
                "name": "St. John Episcopal Church Parish Hall",
            }
        else:
            return {
                "address": "3525 W. Peterson Ave, #306 Chicago, IL 60659",
                "name": "North River EMHSP governing commission office",
            }

    def _index_parse_location(self, item):
        place = item.re("<br>Place: (?P<location>[a-zA-Z0-9 ]+(?!\\\\<br\\\\>))")[0]
        # Leaving "name" value empty for now..
        return {"name": "", "address": place}

    def _minutes_parse_links(self, item, response):
        """Parse or generate links."""
        return [{"href": response.urljoin(item.attrib["href"]), "title": "Minutes"}]

    def _index_parse_links(self, item, response):
        return [
            {
                "title": link.css("::text").get(),
                "href": response.urljoin(link.attrib["href"]),
            }
            for link in item.css("a")
        ]
