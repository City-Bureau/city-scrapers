import re
from datetime import datetime
from io import BytesIO

import requests
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text


class ChiNortheasternIlUniversitySpider(CityScrapersSpider):
    name = "chi_northeastern_il_university"
    agency = "Northeastern Illinois University"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.neiu.edu/about/board-of-trustees/board-meeting-materials"]

    def parse(self, response):
        for meeting in response.css("div.board-meeting-materials-row.views-row"):
            head = meeting.css("h4.accordion::text").get().split()
            if len(head) >= 3:
                date = ' '.join(head[:3])
                title = ' '.join(head[3:]) if len(head) > 3 else ""
            else:
                date = head
                title = ""
            links, agenda = self._parse_links(meeting)
            details = None
            if (agenda):
                res = requests.get(agenda)
                details = extract_text(BytesIO(res.content))
            meeting = Meeting(
                title=self._parse_title(title),
                description="",
                classification=self._parse_classification(title),
                start=self._parse_start(date, details),
                end=self._parse_end(date, details),
                all_day=self._parse_all_day(meeting),
                time_notes="",
                location=self._parse_location(details),
                links=links,
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def getMeetingDetails(self, response):
        print(response.text)

    def _parse_title(self, item):
        return item if not item == "" else "BOARD MEETING"

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        return COMMITTEE if "COMMITTEE" in item else BOARD

    def _parse_start(self, date, parse):
        p = re.compile(r'\d{1,2}:\d{1,2}.[a-z]{0,1}\.{0,1}[a-z]{0,1}\.{0,1}', re.MULTILINE)
        replacementPattern = re.compile('[^0-9:].*')
        time = re.search(p, parse).group(0)
        midDay = re.search(replacementPattern, time).group(0)
        trueTime = time.replace(midDay, " AM").strip() if "a" in midDay else time.replace(midDay, " PM").strip()
        fullDate = date + " " + trueTime
        return datetime.strptime(fullDate, "%B %d, %Y %I:%M %p")

    def _parse_end(self, date, parse):
        pattern = re.compile(r'\d{1,2}:\d{1,2}.[a-z]{0,1}\.{0,1}[a-z]{0,1}\.{0,1}', re.MULTILINE)
        replacementPattern = re.compile('[^0-9:].*')
        time = re.findall(pattern, parse)[-1]
        midDay = re.search(replacementPattern, time).group(0)
        trueTime = time.replace(midDay, " AM").strip() if "a" in midDay else time.replace(midDay, " PM").strip()
        fullDate = date + " " + trueTime
        return datetime.strptime(fullDate, "%B %d, %Y %I:%M %p")

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        pattern = re.compile(r'(\d\d\d\d.*\n?)(?=\s*Meeting)', re.MULTILINE)
        match = re.search(pattern, item)
        location = match.group(1).strip().split('|')
        return {
            "address": location[0].strip() + ", " + location[1].strip(),
            "name": location[2].strip(),
        }

    def _parse_links(self, item):
        links = []
        agenda = None
        for link in item.css("a"):
            href = link.attrib["href"]
            title = link.xpath("./text()").extract_first(default="")
            if "agenda" in title.lower():
                agenda = href
            links.append(
                {
                    "href": href,
                    "title": title,
                }
            )
        return links, agenda

    def _parse_source(self, response):
        return response.url
