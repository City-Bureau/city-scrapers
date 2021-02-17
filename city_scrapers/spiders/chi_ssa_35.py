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
        content = []
        _year = None
        _type = ""
        _description = ""

        content_div = response.css("div.content_block.content.background_white")
        inner_elements = content_div.css("h4, li, p")

        for element in inner_elements:
            element_content = {}

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
                element_content["date"] = element.css("::text").get()
                if "href" in element.get():
                    element_content["url"] = element.css("a::attr(href)").get()

            if "<p><a" in element.get():
                element_content["date"] = element.css("::text").get()
                element_content["url"] = element.css("a::attr(href)").get()

            element_content["description"] = _description
            element_content["type"] = _type
            element_content["year"] = _year
            content.append(element_content)

        self._add_year_to_date_item(content)
        self._parse_date_to_datetime(content)

        for item in content:
            if "date" not in item:
                continue

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

    def _add_year_to_date_item(self, content):
        for item in content:
            if "date" in item:
                if str(item["year"]) not in item["date"]:
                    item["date"] = f"{item['date']} {item['year']}"

                item["date"] = item["date"].replace(",", "")
                item["date"] = item["date"].strip()

    def _parse_date_to_datetime(self, content):
        for item in content:
            if "date" in item:
                _date = item["date"].split()

                if len(_date) == 3:
                    item["date_obj"] = datetime.strptime(item["date"], "%B %d %Y")
                elif len(_date) == 4:
                    item["date_obj"] = datetime.strptime(item["date"], "%A %B %d %Y")
                elif len(_date) == 6:
                    item["date_obj"] = datetime.strptime(
                        item["date"], "%A %B %d (%I:%M %p) %Y"
                    )

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
