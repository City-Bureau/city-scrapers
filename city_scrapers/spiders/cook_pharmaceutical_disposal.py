from datetime import datetime, time

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookPharmaceuticalDisposalSpider(CityScrapersSpider):
    name = "cook_pharmaceutical_disposal"
    agency = "Cook County Pharmaceutical Disposal Advisory Committee"
    timezone = "America/Chicago"
    start_urls = ["https://www.cookcountysheriff.org/rx/advisory-committee/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self.base_url = "https://www.cookcountysheriff.org"

        # Link to current meeting shown as a single image
        # In case you want to proceed with image OCR
        # image_url = base_url +
        #    response.xpath("//div[@class='col-sm-12 ']/h1/img/@src").get()
        # image_response = requests.get(image_url)
        # print(image_to_string(Image.open(BytesIO(image_response.content)),lang='eng'))

        # Scraping past meetings
        for item in response.xpath("//div[@class='col-sm-12 ']/p"):
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
        return "Cook County Safe Disposal of Pharmaceuticals Advisory Committee"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        # Dates are not correct for some meetings as they
        # are not provided in the URL
        # Dates format is not consistent in the URLs
        report_obj = item.xpath(".//a/@href")[0]
        report_desc = report_obj.get().split("/")[-1].split("-")
        if report_desc[2].isdigit():
            date_str = report_desc[0][:-1] + report_desc[1] + report_desc[2]
            date_obj = datetime.strptime(date_str, "%b%d%Y").date()
        elif report_desc[-3].isdigit():
            date_str = report_desc[-3] + report_desc[-2] + report_desc[-1][:-4]
            date_obj = datetime.strptime(date_str, "%m%d%y").date()
        else:
            date_str = report_desc[-2] + report_desc[-1][:-4]
            date_obj = datetime.strptime(date_str, "%m%y").date()
        return datetime.combine(date_obj, time(13))

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "See agenda to confirm times"

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "Conference Room of 704 Daley Center, Chicago, Illinois 60602",
            "name": "Conference Room of 704 Daley Center",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = list()
        for report_obj in item.xpath(".//a/@href"):
            report_desc = report_obj.get().split("/")[-1]
            links.append(
                {
                    "href": self.base_url + report_obj.get(),
                    "title": report_desc[:-4].replace("-", " "),
                }
            )
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
