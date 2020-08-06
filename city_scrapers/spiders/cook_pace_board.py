import re
from datetime import datetime

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookPaceBoardSpider(CityScrapersSpider):
    name = "cook_pace_board"
    agency = "Pace Suburban Bus Services"
    timezone = "America/Chicago"
    start_urls = ["https://www.pacebus.com/public-meetings"]
    location = {
        "name": "Pace Headquarters",
        "address": "550 W Algonquin Rd Arlington Heights, IL 60005",
    }

    def parse(self, response):
        yield from self._parse_meeting_list(response)

        for next_link in response.css("a[rel='next']"):
            yield response.follow(next_link.attrib["href"], callback=self.parse)

    def _parse_meeting_list(self, response):
        for detail_link in response.css("article .more-link"):
            yield response.follow(
                detail_link.attrib["href"], callback=self._parse_detail
            )

    def _parse_detail(self, response):
        classification = self._parse_classification(response)
        meeting = Meeting(
            title=self._parse_title(response, classification),
            description=self._parse_description(response),
            classification=classification,
            start=self._parse_start(response),
            end=self._parse_end(response),
            all_day=False,
            time_notes="",
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)

        yield meeting

    def _parse_title(self, response, classification):
        """Parse or generate meeting title."""
        title_str = response.css("article h1 *::text").extract_first().strip()
        agency_str = response.css(".bar h2 *::text").extract_first().strip()
        if classification in [BOARD, COMMITTEE] or "Citizens" in title_str:
            return agency_str
        return title_str

    def _parse_description(self, response):
        return "\n".join(
            [
                re.sub(r"\s+", " ", p).strip()
                for p in response.css("article .field--name-body p::text").extract()
            ]
        )

    def _parse_classification(self, response):
        """Parse or generate classification from allowed options."""
        subagency_str = response.css(".bar h2::text").extract_first().strip().lower()
        if "citizens" in subagency_str or "advisory" in subagency_str:
            return ADVISORY_COMMITTEE
        if "public" in subagency_str:
            return FORUM
        if "committee" in subagency_str:
            return COMMITTEE
        return BOARD

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        day_dt_str = response.css(
            ".field--name-field-start-date time::text"
        ).extract_first()
        return self._parse_datetime(day_dt_str)

    def _parse_end(self, response):
        day_dt_str = response.css(
            ".field--name-field-end-date time::text"
        ).extract_first()
        if not day_dt_str:
            return
        return self._parse_datetime(day_dt_str)

    def _parse_datetime(self, day_dt_str):
        return datetime.strptime(
            day_dt_str.split(", ")[-1].lower(), "%m/%d/%Y - %I:%M %p"
        )

    def _parse_location(self, response):
        """Parse or generate location."""
        location_name = ""
        location_detail = ""
        for detail in response.css(".bar .row-two .value *::text").extract():
            if not location_name:
                location_name = re.sub(r"\s+", " ", detail).strip()
            else:
                location_detail = re.sub(r"\s+", " ", detail).strip()
        if location_detail:
            location_name = " ".join([location_name, location_detail])
        loc_addr = ""
        if "Headquarters" in location_name:
            loc_addr = self.location["address"]

        return {"name": location_name, "address": loc_addr}

    def _parse_links(self, response):
        """Parse or generate links."""
        links = []
        for link in response.css(".documents .list a, .field--type-link a"):
            link_text = " ".join(link.css("*::text").extract()).strip()
            links.append(
                {"title": link_text, "href": response.urljoin(link.attrib["href"])}
            )
        return links
