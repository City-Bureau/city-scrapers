from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from city_scrapers_core.constants import ADVISORY_COMMITTEE


class ChiDesignSpider(CityScrapersSpider):
    name = "chi_design"
    agency = "Chicgo committee on Design"
    timezone = "America/Chicago"
    start_urls = ["https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design.html"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting_links = self._get_meeting_links(response)
        yield from response.follow_all(meeting_links,
                                       callback=self.parse_meeting)

    def parse_meeting(self, response):
        descriptions = response.css("td:nth-child(2) p::text").getall()
        locations = response.css("td:nth-child(1) p").getall()
        for description, location in zip(descriptions, locations):
            meeting = Meeting(
                title="Committee on Design",
                description=description,
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(response),
                end=self._parse_end(response),
                all_day=self._parse_all_day(response),
                time_notes=self._parse_time_notes(response),
                location=self._parse_location(location),
                links=self._parse_links(response),
                source=self._parse_source(response),
            )
            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            yield meeting

    def _get_meeting_links(self, response):
        meetings = response.css("td p a")
        meeting_links = [link for link in meetings if link.css("::text").get() == "Agenda"]
        return meeting_links

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        item = item.lstrip("<p>")
        item = item.rstrip("</p>")
        item = item.replace("<br>", "")
        return {
            "address": item,
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
