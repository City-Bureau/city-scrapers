from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil import parser


class WayneLocalEmergencyPlanningSpider(CityScrapersSpider):
    name = "wayne_local_emergency_planning"
    agency = "Wayne County Local Emergency Planning Committee"
    timezone = "America/Detroit"
    allowed_domains = ["www.waynecounty.com"]
    start_urls = ["https://www.waynecounty.com/departments/hsem/wayne-county-lepc.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        # the meeting dates I've seen all had the substring 'day, ' as in 'Wednesday, March 6, 2019'
        meeting_dates = response.xpath('''//p[contains(text(),'day, ')]''')

        for item in meeting_dates:
            # clean off the paragraph tags from the parsed meeting date (item)
            item = str(item.extract()).replace('<p>', '').replace('</p>', '')
            # print('------------')
            # print(item)

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

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        prefix = 'Wayne County LEPC Meeting - '
        # create a unique title for each meeting by combining
        # a meaningful prefix with a specific meeting date
        ret_val = prefix + item
        return ret_val

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""  # no description of this specific meeting is shown, so we return an empty string

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        dt = parser.parse(item + " 2pm")  # all meetings will be at 2pm
        return dt

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None  # no end time is shown on the webpage

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "The Wayne County LEPC meets quarterly. All meetings will be at 2:00 p.m."

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False  # Since the meetings start at 2pm, I assume this must be False

    def _parse_location(self, item):
        """Parse or generate location."""
        ''' from webpage:
            Wayne County Community College, 21000 Northline Road, Taylor,
            in the MIPSE Building. The MIPSE Building is the fire training
            facility located at the rear of the campus.'''
        return {
            "address": "21000 Northline Road, Taylor, MI",
            "name": "Wayne County Community College, in the MIPSE Building",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return []  # I didn't see any links for minutes or agendas

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url  # I did't see a more specific detail page
