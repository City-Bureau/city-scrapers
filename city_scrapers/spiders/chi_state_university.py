import re
from calendar import month_name
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiStateUniversitySpider(CityScrapersSpider):
    name = "chi_state_university"
    agency = "Chicago State University"
    timezone = "America/Chicago"
    start_urls = ["https://www.csu.edu/boardoftrustees/dates.htm"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        for data in response.xpath("/html/body/div/div[4]/div/div[1]/div/div"):
            titles = data.xpath(".//label/text()").extract()

            for i, tab in enumerate(data.xpath('.//div[@class = "itd-tab"]')):

                for item in tab.xpath(".//li"):

                    months = {m.lower() for m in month_name[1:]}
                    text = item.xpath(".//text()").extract()[0]
                    monthMatch = next(
                        (word for word in text.split() if word.lower() in months), None
                    )
                    if monthMatch is None:
                        continue

                    meeting = Meeting(
                        title=titles[i],
                        description=self._parse_description(item),
                        classification=self._parse_classification(i),
                        start=self._parse_start(item),
                        end=None,
                        all_day=False,
                        time_notes=self._parse_time_notes(item),
                        location=self._parse_location(item),
                        links=self._parse_links(item),
                        source=self._parse_source(response),
                    )
                    meeting["status"] = self._get_status(meeting)
                    meeting["id"] = self._get_id(meeting)

                    yield meeting

    def _parse_description(self, item):
        parts = item.xpath(".//text()").extract()
        description = "".join([str(x) for x in parts])
        description = (
            description.replace("\xa0", " ")
            .replace("\n", " ")
            .replace("                                     ", " ")
            .replace("\t", " ")
            .strip()
        )
        return description

    def _parse_classification(self, i):
        classifications = [BOARD, BOARD, COMMITTEE]
        return classifications[i]

    def _parse_start(self, item):
        text = item.xpath(".//text()").extract()[0]
        text = text.replace("\xa0", "").strip()

        today = datetime.now()
        yearMatch = today.year
        monthMatch = today.month
        dayMatch = today.day
        hourMatch = 0
        minuteMatch = 0

        try:
            yearMatch = int(re.search(r"\d{4}", text).group(0))
        except AttributeError:
            pass

        try:
            dayMatch = int(re.search(r"\d{1,2}", text).group(0))
        except AttributeError:
            pass

        try:
            months = {m.lower() for m in month_name[1:]}
            monthMatch = next(
                (word for word in text.split() if word.lower() in months), None
            )
            monthMatch = datetime.strptime(monthMatch, "%B").month
        except AttributeError:
            pass

        try:
            minuteMatch = re.search(r":([0-5][0-9])", text).group(0)
            minuteMatch = int(minuteMatch.replace(":", ""))
        except AttributeError:
            pass

        try:
            hourMatch = re.search(r"(1[0-2]|0?[1-9]):", text).group(0)
            hourMatch = int(hourMatch.replace(":", ""))
        except AttributeError:
            pass

        if "p.m." in text:
            hourMatch += 12

        return datetime(yearMatch, monthMatch, dayMatch, hourMatch, minuteMatch)

    def _parse_time_notes(self, item):
        text = " ".join(item.xpath(".//text()").extract())
        text = text.replace("\xa0", "").strip()

        notes = ""
        if "reschedule" in text.lower() or "postpone" in text.lower():
            notes = text
        if "tbd" in text.lower():
            notes = "Meeting time TBD"
        return notes

    def _parse_location(self, item):

        return {
            "address": "9501 S. King Drive Chicago, IL 60628",
            "name": "Room 15, 4th Floor, Gwendolyn Brooks Library Auditorium",
        }

    def _parse_links(self, item):

        try:
            link = item.xpath(".//a").attrib["href"]
        except KeyError:
            link = ""
        title = ""
        for search in ["webinar", "zoom", "meeting"]:
            if search in link:
                title = "Virtual meeting link"

        return [{"href": link, "title": title}]

    def _parse_source(self, response):
        return response.url
