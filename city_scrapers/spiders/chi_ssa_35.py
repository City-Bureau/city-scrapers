from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa35Spider(CityScrapersSpider):
    name = "chi_ssa_35"
    agency = "Chicago Special Service Area #35 Lincoln Ave"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.lincolnparkchamber.com/"
        + "businesses/special-service-areas/lincoln-avenue-ssa/ssa-administration/"
    ]

    def parse(self, response):
        _year = None
        _type = ""
        _description = ""

        content_div = response.css("div.content_block.content.background_white")
        inner_elements = content_div.css("h4, li, p")

        for element in inner_elements:
            meeting_content = {}

            if "<h4>" in element.get():
                # Type here could be Schedule, Agendas or Minutes
                title = element.css("::text").get().split()
                _type = title[-1]
                try:
                    _year = int(title[0])
                except ValueError:
                    _year = None

            if "<p><em>" in element.get():
                # The encode part here is to remove \xa0 and other characters like that
                _description = (
                    element.css("::text").get().encode("ascii", "ignore").decode()
                )

            if "<li>" in element.get():
                meeting_content["date"] = element.css("::text").get()
                if "href" in element.get():
                    meeting_content["url"] = element.css("a::attr(href)").get()

            if "<p><a" in element.get():
                meeting_content["date"] = element.css("::text").get()
                meeting_content["url"] = element.css("a::attr(href)").get()

            meeting_content["description"] = _description
            meeting_content["type"] = _type
            meeting_content["year"] = _year

            if "date" not in meeting_content:
                continue
            else:
                meeting_content["date"] = self._add_year_to_date_item(meeting_content)
                meeting_content["date_obj"] = self._parse_date_to_datetime(
                    meeting_content
                )

            meeting = Meeting(
                title=self._parse_title(meeting_content),
                description=self._parse_description(meeting_content),
                classification=self._parse_classification(meeting_content),
                start=self._parse_start(meeting_content),
                end=self._parse_end(meeting_content),
                all_day=self._parse_all_day(meeting_content),
                time_notes=self._parse_time_notes(meeting_content),
                location=self._parse_location(meeting_content),
                links=self._parse_links(meeting_content),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _add_year_to_date_item(self, content):
        if "date" in content:
            _date = content["date"]

            if str(content["year"]) not in content["date"]:
                _date = f"{content['date']} {content['year']}"

            _date = _date.replace(",", "")
            return _date.strip()

    def _parse_date_to_datetime(self, content):
        if "date" in content:
            _date = content["date"].split()

            if len(_date) == 3:
                return datetime.strptime(content["date"], "%B %d %Y")
            elif len(_date) == 4:
                return datetime.strptime(content["date"], "%A %B %d %Y")
            elif len(_date) == 6:
                return datetime.strptime(content["date"], "%A %B %d (%I:%M %p) %Y")

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Commission"

    def _parse_description(self, item):
        """Parse or generate meeting title."""
        return item["description"]

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return item["date_obj"]

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return item["date_obj"] + timedelta(minutes=90)

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "Confirm with agency",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": item.get("url"), "title": item["date"]}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
