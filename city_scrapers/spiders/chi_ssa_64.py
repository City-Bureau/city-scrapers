import html
import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa64Spider(CityScrapersSpider):
    name = "chi_ssa_64"
    agency = "Chicago Special Service Area #64 Walden Parkway"
    timezone = "America/Chicago"
    start_urls = ["https://www.mpbhba.org/business-resources/"]

    def parse(self, response):
        meetings = self._parse_block(response)
        for item in meetings:
            meeting = Meeting(
                title="Commission",
                description="",
                classification=COMMISSION,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=[],
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_block(self, response):
        """Parse data in specific SSA 20 meetings block."""
        result = []
        aux = []
        meetings = []
        count = 0
        general_block = response.xpath(
            '//*[@class="et_pb_module et_pb_text et_pb_text_2 '
            'et_pb_text_align_left et_pb_bg_layout_light"]'
        )
        years = general_block.xpath(
            './/*[@class="et_pb_text_inner"]/h3/text()'
        ).extract()
        specific_block = (
            general_block.xpath('.//*[@class="et_pb_text_inner"]')
            .extract_first()
            .split("<strong>")
        )
        for line in specific_block:
            if "SSA 64:" in line:
                result.append(line.split("</p><p>"))

        for meetings_list in result:
            year = years[count][0:4]
            for meeting in meetings_list:
                meeting = (
                    meeting.replace("<br>", "").replace("SSA 64:</strong>", "").strip()
                )
                if meeting != "" and "</p></div>" not in meeting:
                    aux.append(year)
                    aux.append(html.unescape(meeting))
            count += 1

        for i in range(0, len(aux), 2):
            meetings.append(aux[i : i + 2])

        return meetings

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        time_zone = "AM" if ("a.m." in item[1]) else "PM"
        result = re.split("a.m.|p.m.", item[1])[0].split(",")
        date_string = (
            item[0]
            + result[1]
            + " "
            + time_zone
            + " "
            + item[1].split("a.m.")[0].split(",")[2].strip()
        )
        start = datetime.strptime(date_string, "%Y %B %d %p %H")

        return start

    def _parse_location(self, item):
        """Parse or generate location."""
        result = (
            item[1].strip() + " Chicago, IL"
            if ("Chicago, IL" not in item[1].strip())
            else item[1].strip()
        )
        result = re.split("a.m.|p.m.", result)[1]

        return {
            "address": ",".join(result.split(",")[1:]).strip(),
            "name": result.split(",")[0].strip(),
        }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
