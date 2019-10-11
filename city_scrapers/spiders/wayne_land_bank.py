import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.http import FormRequest


class WayneLandBankSpider(CityScrapersSpider):
    name = "wayne_land_bank"
    agency = "Wayne County Land Bank"
    timezone = "America/Detroit"
    allowed_domains = ["public-wclb.epropertyplus.com"]
    start_urls = ["https://public-wclb.epropertyplus.com/landmgmtpub/app/base/customPage"]
    location = {
        "name": "Wayne County Treasurer's Office",
        "address": "400 Monroe St 5th Floor, Detroit, MI 48226, United States",
    }

    def start_requests(self):
        yield FormRequest(
            self.start_urls[0],
            formdata={
                "templateName": "BoardofDirectors",
                "title": "Board+of+Directors"
            },
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        data = response.xpath('//script[@id="custom_page_template"]/text()').extract()
        data = re.findall(
            '(Jan(?:uary)|Feb(?:ruary)|Mar(?:ch)|Apr(?:il)|May|Jun(?:e)|Jul(?:y)'
            '|Aug(?:ust)|Sep(?:tember)|Oct(?:ober)|Nov(?:ember)|Dec(?:ember))'
            r'(.*?)(?=\.\s|\\n)'
            '(.*?)(?=\\n)', data[0]
        )

        for item in data:
            meeting = Meeting(
                title=item[2].strip(" .()"),
                description="",
                classification=BOARD,
                start=self._parse_start("".join(item[0:2])),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(""),
                links=[],
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        item = item.replace('p.m', 'pm')
        item = item.replace('a.m', 'am')
        item = re.sub(r':\d{1,2}', '', item)
        start_datetime = datetime.strptime(item, "%B %d, %Y at %I %p")
        return start_datetime

    def _parse_location(self, item):
        """Parse or generate location."""
        return self.location
