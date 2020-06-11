import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlPoliceProfessionalismSpider(CityScrapersSpider):
    name = "il_police_professionalism"
    agency = "Illinois Commission on Police Professionalism"
    timezone = "America/Chicago"
    start_urls = ["https://www.isp.state.il.us/media/openmtgs.cfm"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        list_items = response.xpath("//li[contains(@style,'padding-bottom')]")
        relavent_links = list_items.xpath(
            'a[(.//*|.)[contains(text(),"Police Professionalism")]]/@href'
        ).extract()
        for i in range(0, len(relavent_links)):
            link = response.urljoin(relavent_links[i])
            yield response.follow(link, self._parse_item)

    def _parse_item(self, response):
        """`_parse_item` should always `yield` Meeting items"""
        paragraphs = response.xpath("//p")
        title = response.xpath("//h3/text()").get()
        meeting = Meeting(
            title=self._parse_title(response),
            description=self._parse_description(response, paragraphs),
            classification=self._parse_classification(title),
            start=self._parse_start(response, paragraphs),
            end=None,
            time_notes="",
            all_day=False,
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=response.url,
        )
        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting, title)
        return meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Commission on Police Professionalism"

    def _parse_description(self, item, paragraphs):
        return_list = []
        for i in paragraphs:
            xpath_selector = i.xpath("text()").get()
            if xpath_selector is not None:
                return_list.append(xpath_selector.strip().replace("\xa0", ""))
        """Parse or generate meeting description."""
        return " ".join(return_list)

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item, paragraphs):
        """Parse start datetime as a naive datetime object."""
        final_date = "March 28, 2019"
        final_time = "2:00 PM"
        for p in paragraphs.getall():
            date_match = re.search(r"[a-zA-Z]{3,10} \d{1,2}([a-z]{2})?,? \d{4}", p)
            time_match = re.search(r"\d{1,2}(:\d{2})? ?[apm\.]{2,4}", p)
            if date_match:
                final_date = date_match.group(0)
            if time_match:
                final_time = time_match.group(0).replace(".", "").upper()
        final_datetime = final_date + " " + final_time
        final_datetime = datetime.strptime(final_datetime, "%B %d, %Y %I:%M %p")
        return final_datetime

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "301 S 2nd St, Springfield, IL 62701",
            "name": "Illinois State Capitol",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": item.url, "title": "Agenda"}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
