import re
from calendar import day_name, month_name
from collections import defaultdict
from datetime import date, datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiStateUniversitySpider(CityScrapersSpider):
    name = "chi_state_university"
    agency = "Chicago State University"
    timezone = "America/Chicago"
    start_urls = [f"https://www.csu.edu/boardoftrustees/\
        meetingagendas/year{date.today().year}.htm"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self.minutes_map = self._parse_minutes(response)
        yield scrapy.Request(
            "https://www.csu.edu/boardoftrustees/dates.htm",
            callback=self._parse_meetings,
            dont_filter=True
        )

    def _parse_minutes(self, response):

        minutes_map = defaultdict(list)

        for data in response.xpath("/html/body/div/div[4]/div/div[1]/div"):
            for p in data.xpath(".//p"):
                title = p.xpath(".//text()").extract()[0]
                if "Meetings" in title:
                    meetings = p.xpath("following-sibling::*")
                    for meeting in meetings.xpath(".//li"):
                        link = meeting.xpath(".//a").attrib["href"]
                        dateStr = meeting.xpath(".//text()").extract()[0]
                        dateStr = re.sub(",", " ", dateStr)
                        dateStr = re.sub(r"\s+", " ", dateStr)

                        commonStrings = \
                            ["Standing Committee", "Special Board", "Full Board"]

                        for i in commonStrings:
                            if i in title:
                                title = i

                        minutes_map[title + " " + dateStr].append(
                            {
                                "title": title + " " + dateStr,
                                "href": "https://www.csu.edu" + link,
                            }
                        )
            return minutes_map

    def _parse_meetings(self, response):
        for data in response.xpath("/html/body/div/div[4]/div/div[1]/div/div"):
            for label in data.xpath(".//label"):
                title = label.xpath(".//text()").extract()[0]
                sibling = label.xpath("following-sibling::*")
                self._validate_location(sibling)
                for item in sibling.xpath(".//li"):
                    months = {m.lower() for m in month_name[1:]}
                    text = item.xpath(".//text()").extract()[0]
                    monthMatch = next(
                        (word for word in text.split() if word.lower() in months), None
                    )
                    if monthMatch is None:
                        continue
                    start = self._parse_start(item)

                    meeting = Meeting(
                        title=title,
                        description=self._parse_description(item),
                        classification=self._parse_classification(title),
                        start=start,
                        end=None,
                        all_day=False,
                        time_notes=self._parse_time_notes(item),
                        location=self._parse_location(item),
                        links=self._parse_links(item, title, start),
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
            .replace("\t", " ")
            .strip()
        )
        description = re.sub(r"\s+", " ", description)
        return description

    def _parse_classification(self, title):
        if "board" in title.lower():
            return BOARD
        if "committee" in title.lower():
            return COMMITTEE
        return ""

    def _parse_start(self, item):
        text = item.xpath(".//text()").extract()[0]
        text = text.replace("\xa0", " ").replace(
            "@", "").replace(",", "").replace(".", "")

        days = {m.lower() for m in day_name}
        dayMatch = next(
            (word for word in text.split() if word.lower() in days), None
        )
        if dayMatch:
            text = text.replace(dayMatch, "")
        text = re.sub(r"\s+", " ", text).strip()
        months = {m.lower() for m in month_name}
        textParts = []
        for word in text.split():
            if word.lower() in months:
                textParts.append(word)
            if word.isnumeric():
                textParts.append(word)
            if ':' in word:
                textParts.append(word)
            if word in ['am', 'pm']:
                textParts.append(word)
        dateStr = []
        for word in textParts:
            if word not in dateStr:
                dateStr.append(word)
        dateStr = ' '.join(dateStr)

        try:
            start = datetime.strptime(dateStr, "%B %d %Y %I:%M %p")
        except ValueError:
            start = datetime.strptime(dateStr , "%B %d %Y")

        return start

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

    def _validate_location(self, item):
        if "Room 415" not in " ".join(item.xpath(".//text()").extract()):
            raise ValueError("Meeting location has changed")

    def _parse_links(self, item, title, start):

        try:
            link = item.xpath(".//a").attrib["href"]
        except KeyError:
            link = ""
        linkTitle = f"{link}"
        for search in ["webinar", "zoom", "meeting"]:
            if search in link:
                linkTitle = "Virtual meeting link"
        commonStrings = ["Standing Committee", "Special Board", "Full Board"]

        for i in commonStrings:
            if i in title:
                title = i

        if self.minutes_map[title + " " + start.strftime("%B %d %Y")]:
            minutes = self.minutes_map[title + " " + start.strftime("%B %d %Y")]
            return [{"href": link, "title": linkTitle, "minutes": minutes}]

        return [{"href": link, "title": linkTitle}]

    def _parse_source(self, response):
        return response.url
