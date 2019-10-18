import re

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetRegionalTransitAuthoritySpider(CityScrapersSpider):
    name = "det_regional_transit_authority"
    agency = "Regional Transit Authority of Southeast Michigan"
    timezone = "America/Detroit"
    start_urls = ["http://www.rtamichigan.org/board-committee-meetings/"]
    location = {
        "name": "RTA Office",
        "address": "1001 Woodward Ave, Suite 1400, Detroit, MI 48226",
    }

    def parse(self, response):
        for section in response.css(".elementor-accordion-item"):
            title = self._parse_title(section)
            for item in section.css("tr")[1:]:
                start = self._parse_start(item)
                if not start:
                    continue
                meeting = Meeting(
                    title=title,
                    description="",
                    classification=self._parse_classification(title),
                    start=start,
                    end=None,
                    time_notes="",
                    all_day=False,
                    location=self.location,
                    links=self._parse_links(item),
                    source=response.url,
                )
                meeting["status"] = self._get_status(
                    meeting, text=" ".join(item.css("*::text").extract())
                )
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_title(self, item):
        return re.sub(r"\s+", " ",
                      " ".join(item.css(".elementor-tab-title *::text").extract())).strip()

    @staticmethod
    def _parse_classification(title):
        if "Advisory" in title:
            return ADVISORY_COMMITTEE
        if "Committee" in title:
            return COMMITTEE
        return BOARD

    @staticmethod
    def _parse_start(item):
        """
        Parse start date and time.
        """
        date_str = item.xpath("td[1]/text()").extract_first("")
        time_str = item.xpath("td[2]/text()").extract_first("")
        try:
            return parse("{} {}".format(date_str, time_str))
        except ValueError:
            pass

    @staticmethod
    def _parse_links(item):
        """Parse or generate links."""
        anchors = item.xpath(".//a")
        return [{
            "href": anchor.xpath("@href").extract_first(""),
            "title": re.sub(r"\s+", " ",
                            anchor.xpath(".//text()").extract_first("")).strip(),
        } for anchor in anchors]
