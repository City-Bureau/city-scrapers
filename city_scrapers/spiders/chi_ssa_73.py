import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa73Spider(CityScrapersSpider):
    name = "chi_ssa_73"
    agency = "Chicago Special Service Area #73 Chinatown"
    timezone = "America/Chicago"
    start_urls = ["https://chinatownssa73.org/meeting-schedule/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        linksList = self._get_links(response)
        location = self._parse_location(response)
        idsList = []
        startTime = self._parse_time(response)
        for item in response.css("article p"):
            start = self._parse_start(item, startTime)
            if not start:
                continue
            meeting = Meeting(
                title="SSA #73 Chinatown Board",
                description="",
                classification=BOARD,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(item, start, linksList),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            if meeting["id"] in idsList:
                continue
            else:
                idsList.append(meeting["id"])

            yield meeting

    def _parse_start(self, item, startTime):
        """
        Parse start date and time.
        """
        date_str = item.css("*::text").extract_first()
        date_match = re.search(r"\w{3,9} \d{1,2}, \d{4}", date_str)
        if date_match:
            parsed_date = datetime.strptime(date_match.group(), "%B %d, %Y")
            return datetime.combine(parsed_date.date(), startTime.time())

    def _parse_time(self, response):
        firstLine = response.css("article p").extract_first()
        time_match = re.search(r"\d{1,2}:\d{2} [ap]\.m", firstLine)
        if time_match:
            tempStr = time_match.group()
            tempStr = tempStr.replace(".", "")
            tempStr = tempStr.upper()
            return datetime.strptime(tempStr, "%I:%M %p")
        else:
            return time(18, 30)

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        if "1700 S. Wentworth" in response.text:
            return {
                "address": "1700 S. Wentworth Avenue, Chicago, Illinois",
                "name": "Leonard M. Louie Fieldhouse",
            }
        else:
            raise ValueError("Meeting address has changed")

    def _get_links(self, response):
        linksList = []
        for item in response.css("a"):
            newDict = {}
            addLink = False
            if "Agenda" in item.extract():
                newDict["title"] = "Agenda"
                addLink = True
            elif "Minutes" in item.extract():
                newDict["title"] = "Minutes"
                addLink = True
            if addLink:
                newDict["href"] = item.attrib["href"]
                rawRef = item.css("*::text").extract_first()
                newDict["date"] = rawRef.split()[1]
                linksList.append(newDict)
        return linksList

    def _parse_links(self, item, start, linksList):
        """Parse or generate links."""
        resultList = []
        targetStr1 = start.strftime("%m-%d-%Y").replace(" 0", " ")
        targetStr2 = start.strftime("%m-%d-%y").replace(" 0", " ")
        for item in linksList:
            if item["date"] in targetStr1 or item["date"] in targetStr2:
                newDict = {}
                newDict["href"] = item["href"]
                newDict["title"] = item["title"]
                resultList.append(newDict)
        return resultList
