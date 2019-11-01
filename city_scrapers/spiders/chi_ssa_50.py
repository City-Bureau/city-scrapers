from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime


class ChiSsa50Spider(CityScrapersSpider):
    name = "chi_ssa_50"
    agency = "Chicago Special Service Area"
    timezone = "America/Chicago"
    start_urls = ["http://southeastchgochamber.org/special-service-area-50/"]
    base_xpath = '//div[@class="entry-content"]'
    item_xpath = base_xpath + '//p[@style="text-align: center;"]/text()'

    def parse(self, response):
        title = self._parse_title(response)
        description = self._parse_description(response)

        for item in response.xpath(self.item_xpath).getall():
            meeting = Meeting(
                title=title,
                description=description,
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(),
                time_notes=self._parse_time_notes(),
                location=self._parse_location(),
                links=self._parse_links(),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, response):
        title = response.css("title::text").get()
        return title

    def _parse_description(self, response):
        description_xpath = '//div[@class="container-fluid page-full-description-above"]'
        description_content = '//div[@class="row"]//div["col-xs-12"]//p/text()'
        description = response.xpath(self.base_xpath + description_xpath + description_content).get()
        return description

    def _parse_classification(self, item):
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        date = datetime.strptime(item, "%B %d, %Y")
        return date

    def _parse_end(self, item):
        date = datetime.strptime(item, "%B %d, %Y")
        return date

    def _parse_time_notes(self):
        return ""

    def _parse_all_day(self):
        return False

    def _parse_location(self):
        return {
            "address": "8334 S Stony Island Ave, Chicago, IL 60617",
            "name": "Southeast Chicago Chamber",
        }

    def _parse_links(self):
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        return response.url
