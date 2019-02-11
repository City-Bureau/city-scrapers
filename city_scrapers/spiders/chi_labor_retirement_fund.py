from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import date, datetime


class ChiLaborRetirementFundSpider(CityScrapersSpider):
    name = "chi_labor_retirement_fund"
    agency = "Laborers' & Retirement Board Employees' Annuity & Benefit Fund"
    timezone = "America/Chicago"
    allowed_domains = ["www.labfchicago.org"]
    start_urls = ["http://www.labfchicago.org/agendas-minutes"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # for item in response.css(".meetings"):
        for item in response.css(".days"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    ###### NEEDS DONE
    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return None

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        pulledDate = item.css('.calendar-day::text').extract_first()
        year = int(pulledDate[7:])
        month = int(pulledDate[0:3])
        day = int(pulledDated[4:6])
        startTime = item.css('li:nth-child(2)::text').extract_first()
        i = 0
        hrs = ''
        while time[i] != ':':
            hrs += time[i]
            i += 1
        i += 1
        hrs = int(hrs)
        minutes = ''
        while time[i] != ' ':
            minutes += time[i]
        minutes = int(minutes)
        i += 1
        if time[i] == 'p':
            hours += 12
        start = datetime.datetime(year, month, day, hours, minutes, 00, 00)
        return start

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
        return {
            "address": "321 N Clark St, Chicago, IL",
            "name": "Fund Office",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
