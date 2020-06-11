from datetime import datetime

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa22Spider(CityScrapersSpider):
    name = "chi_ssa_22"
    agency = "Chicago Special Service Area #22 Clark St/Andersonville"
    timezone = "America/Chicago"
    start_urls = [
        "http://www.andersonville.org/our-organizations/andersonville-ssa-22/"
    ]
    location = {
        "name": "Andersonville Chamber of Commerce",
        "address": "5153 N. Clark St. #228 Chicago, IL 60640",
    }

    def parse(self, response):
        # the address is in a normal paragraph, so whole page is looked at
        self._validate_location(response.body.decode("utf-8"))

        h2s = response.xpath("//h2")

        # Dictionary containing all meeting dictionaries
        # The dates will be the keys
        meetings = dict()

        last_year = datetime.today().replace(year=datetime.today().year - 1)

        for entry_cnt, entry in enumerate(h2s, start=1):
            entry_str = entry.xpath("./text()").extract_first()
            if entry_str and (
                "Meeting Schedule" in entry_str or "Meetings & Minutes" in entry_str
            ):
                year = entry_str[0:4]

                # Only consider ps between two h2s
                for ul in entry.xpath(
                    "following-sibling::ul[count(preceding-sibling::h2)=" "$entry_cnt]",
                    entry_cnt=entry_cnt,
                ):
                    for item in ul.xpath("./li"):

                        item_str = " ".join(
                            item.xpath("./text()").extract_first().split(" ")[0:2]
                        )
                        start = self._parse_start(item_str, year)
                        date = start.date()

                        meetings[date] = {"start": start, "links": []}

                        for a in item.xpath("./a"):

                            item_str = a.xpath("./text()").extract_first()
                            item_links = a.xpath("@href").extract()
                            meetings[date]["links"].extend(
                                self._parse_links(item_links, item_str)
                            )

        # Create the meeting objects
        for key, item in meetings.items():

            if item["start"] < last_year and not self.settings.getbool(
                "CITY_SCRAPERS_ARCHIVE"
            ):
                continue

            meeting = Meeting(
                title="Commission",
                description="",
                classification=COMMISSION,
                start=item["start"],
                end=None,
                time_notes="9:30am or 3:45pm, please contact info@andersonville.org "
                "for more information",
                all_day=False,
                location=self.location,
                links=item["links"],
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_links(self, items, item_str):
        """Parse documents if available on previous board meeting pages"""
        documents = []
        for url in items:
            if url:
                documents.append(self._build_link_dict(url, item_str))

        return documents

    @staticmethod
    def _build_link_dict(url, item_str):
        """Determine link type based on link text content"""
        if "agenda" in item_str.lower():
            return {"href": url, "title": "Agenda"}
        elif "minutes" in item_str.lower():
            return {"href": url, "title": "Minutes"}
        else:
            return {"href": url, "title": "Link"}

    @staticmethod
    def _validate_location(text):
        """Parse or generate location."""
        if "5153" not in text:
            raise ValueError("Meeting location has changed")

    @staticmethod
    def _parse_date(raw_date, year):
        """Parse date."""
        if raw_date:
            return dateutil.parser.parse(year + " " + raw_date)

    def _parse_start(self, item_str, year):
        """Parse start datetime."""
        start = self._parse_date(item_str, year)
        if start:
            return start.replace(hour=0, minute=00)
