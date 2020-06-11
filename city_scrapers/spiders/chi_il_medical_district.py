import re
from collections import defaultdict
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiIlMedicalDistrictSpider(CityScrapersSpider):
    name = "chi_il_medical_district"
    agency = "Illinois Medical District Commission"
    timezone = "America/Chicago"
    start_urls = ["http://medicaldistrict.org/commission/"]
    location = {
        "name": "Illinois Medical District Commission",
        "address": "2100 W Harrison St, Room 106, Chicago, IL 60612",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Generate the mapping of dates to links and a list of upcoming datetimes
        link_date_map = self._parse_link_date_map(response)
        meeting_dt_list = self._parse_upcoming(response)
        meeting_dates = [dt.date() for dt in meeting_dt_list]

        # Create a list of unique dates found including relevant times (with defaults)
        for link_date in link_date_map.keys():
            if link_date not in meeting_dates:
                meeting_dt_list.append(datetime.combine(link_date, time(0)))

        # Iterate through each datetime, parsing details from associated links if found
        for meeting_dt in set(meeting_dt_list):
            meeting_links = link_date_map[meeting_dt.date()]
            meeting = Meeting(
                title=self._parse_title(meeting_links),
                description="",
                classification=self._parse_classification(meeting_links),
                start=meeting_dt,
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=meeting_links,
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, links):
        """Parse or generate meeting title."""
        for link in links:
            if "hearing" in link["title"].lower():
                return link["title"].replace("Notice", "").strip()
            if "special" in link["title"].lower():
                return "Special Meeting"
        return "Illinois Medical District Commission"

    def _parse_classification(self, links):
        """Parse or generate classification from allowed options."""
        for link in links:
            if "hearing" in link["title"].lower():
                return FORUM
        return COMMISSION

    def _parse_start(self, start_str, year=None):
        """Parse start datetime as a naive datetime object."""
        # Allow for overriding year where not provided
        date_re = r"\w+\s+\d{1,2}" if year else r"\w+\s+\d{1,2},\s+\d{4}"
        date_match = re.search(date_re, start_str)
        if not date_match:
            return
        date_str = date_match.group().replace(",", "")
        if year:
            date_str += " {}".format(year)

        time_match = re.search(r"\d{1,2}:\d{2}\s+[APM\.]{2,4}", start_str)
        # Override for defaulting 2019 meetings to 8am, otherwise default to midnight
        if not year or year == "2019":
            time_str = "8:00 AM"
        else:
            time_str = "12:00 AM"
        if time_match:
            time_str = time_match.group().replace(".", "").strip()

        return datetime.strptime(
            "{} {}".format(date_str, time_str), "%B %d %Y %I:%M %p"
        )

    def _parse_upcoming(self, response):
        """Return a list of naive datetimes to upcoming meetings"""
        upcoming_dts = []
        for upcoming in response.css(
            ".vc_col-sm-4.column_container:nth-child(1) .mk-text-block.indent16 p *::text"  # noqa
        ):
            start = self._parse_start(upcoming.extract())
            if start:
                upcoming_dts.append(start)
        return upcoming_dts

    def _parse_link_date_map(self, response):
        """Generate a defaultdict mapping of meeting dates and associated links"""
        link_date_map = defaultdict(list)
        for link in response.css(
            ".vc_col-sm-4.column_container:nth-child(1) .mk-text-block.indent16"
        )[:1].css("a"):
            link_str = link.xpath("./text()").extract_first()
            link_start = self._parse_start(link_str)
            if link_start:
                link_date_map[link_start.date()].append(
                    {
                        "title": re.sub(r"\s+", " ", link_str.split(" – ")[-1]).strip(),
                        "href": link.attrib["href"],
                    }
                )
        for section in response.css(
            ".vc_col-sm-4.column_container:nth-child(1) .vc_tta-panel"
        ):
            year_str = section.css(".vc_tta-title-text::text").extract_first().strip()
            for section_link in section.css("p > a"):
                link_str = section_link.xpath("./text()").extract_first()
                link_dt = self._parse_start(link_str, year=year_str)
                if link_dt:
                    link_date_map[link_dt.date()].append(
                        {
                            "title": re.sub(
                                r"\s+", " ", link_str.split(" – ")[-1]
                            ).strip(),
                            "href": section_link.xpath("@href").extract_first(),
                        }
                    )
        return link_date_map
