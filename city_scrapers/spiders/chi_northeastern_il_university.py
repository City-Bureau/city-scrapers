from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from city_scrapers_core.constants import COMMITTEE, BOARD
from datetime import datetime, time

import requests
from io import BytesIO
from pdfminer.high_level import extract_text
import re
class ChiNortheasternIlUniversitySpider(CityScrapersSpider):
    name = "chi_northeastern_il_university"
    agency = "Northeastern Illinois University"
    timezone = "America/Chicago"
    start_urls = ["https://www.neiu.edu/about/board-of-trustees/board-meeting-materials"]


    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for meeting in response.css("div.board-meeting-materials-row.views-row"):
            # print(meeting)
            head = meeting.css("h4.accordion::text").get().split()
            if len(head) >= 3:
                date = ' '.join(head[:3])
                title = ' '.join(head[3:]) if len(head) > 3 else ""
            else:
                date = head  
                title = ""
            links, agenda  = self._parse_links(meeting)
            
            details = None
            # print("AGENDA: ", agenda)
            if(agenda):
                # details = Request._get_body
                res =  requests.get(agenda)
                details = extract_text(BytesIO(res.content))
            # print("Details:", details)
            # pattern = re.compile("(.*\n?)(?=\s*Meeting)", re.MULTILINE)
            pattern = re.compile(r'\d{1,2}:\d{1,2}.[a-z]{0,1}\.{0,1}[a-z]{0,1}\.{0,1}', re.MULTILINE)
            match = re.search(pattern, details).group(0).strip()
            print("MATCHES: " , match)
            print("REPLACE1: ", pattern)
            # print(match.group(1))
            # print(pattern)
            # match = re.findall(pattern, details).group(0).replace('a.m.', 'AM').replace('p.m.', 'PM')
            # match = re.search(pattern, details).group(0).replace('a.m.', 'AM').replace('p.m.', 'PM').replace('a', " AM").replace('p', ' PM')
            # replacementPattern = re.compile('[^0-9:].*')
            # print("REPLACE: " , replacementPattern)
            # midDay = re.search(replacementPattern, match).group(0)
            # trueDate = match.replace(midDay, " AM").strip() if "a" in midDay else match.replace(midDay, " PM").strip()

            # print(trueDate)
            # x = match.group(0)
            # x = x.replace('a.m.', 'AM').replace('p.m.', 'PM') 
            fullDate = date + " " + match.strip() + " " + self.timezone
            print(fullDate)
            
            # dated = datetime.strptime(fullDate, "%B %d, %Y %I:%M %p %Z")
            # print(dated)
            # test = {"address": match[0] + ", "+ match[1],
            # "name": match[3]}
            # print(test)
            meeting = Meeting(
                title=self._parse_title(title),
                description="",
                classification=self._parse_classification(title),
                start=self._parse_start(date, details),
                end=self._parse_end(date, details),
                all_day=self._parse_all_day(meeting),
                time_notes="",
                location=self._parse_location(details),  #done
                links=links, # done
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting
    def getMeetingDetails(self, response):
        print(response.text)
    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item if not item == "" else "BOARD MEETING" 

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        
        return COMMITTEE if "COMMITTEE" in item else BOARD

    def _parse_start(self, date, parse):
        pattern = re.compile(r'\d{1,2}:\d{1,2}.[a-z]{0,1}\.{0,1}[a-z]{0,1}\.{0,1}', re.MULTILINE)
        replacementPattern = re.compile('[^0-9:].*')
        time = re.search(pattern, parse).group(0)
        midDay = re.search(replacementPattern, time).group(0)
        trueTime = time.replace(midDay, " AM").strip() if "a" in midDay else time.replace(midDay, " PM").strip()

        # midDay = re.search(time, replacementPattern)
        # nightOrDay = time.replace(midDay, " AM").strip() if "a" in midDay.group(0).lower() else time.replace(midDay, " PM")
        # time = re.search(pattern, parse).group(0).replace('a.m.', 'AM').replace('p.m.', 'PM').replace('p', ' PM').replace('a', ' AM').replace("am", " AM").replace("pm", " PM").strip() 
        fullDate = date + " " + trueTime
        # day = datetime.strptime(fullDate, "%B %d, %Y %I:%M %p %Z")

        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(fullDate, "%B %d, %Y %I:%M %p")

    def _parse_end(self, date, parse):
        pattern = re.compile(r'\d{1,2}:\d{1,2}.[a-z]{0,1}\.{0,1}[a-z]{0,1}\.{0,1}', re.MULTILINE)  
        replacementPattern = re.compile('[^0-9:].*')  
        time = re.findall(pattern, parse)[-1]      
        midDay = re.search(replacementPattern, time).group(0)
        trueTime = time.replace(midDay, " AM").strip() if "a" in midDay else time.replace(midDay, " PM").strip()
  
        # time = re.findall(pattern, parse)[-1].replace('a.m.', 'AM').replace('p.m.', 'PM').replace('p', ' PM').replace('a', " AM").replace('am', " AM").replace('pm', " PM").strip()
        fullDate = date + " " + trueTime
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(fullDate, "%B %d, %Y %I:%M %p")

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        pattern = re.compile(r'(\d\d\d\d.*\n?)(?=\s*Meeting)', re.MULTILINE)
        match = re.search(pattern, item)
        location = match.group(1).strip().split('|')
        print("LOCATIONS: " , location)
        """Parse or generate location."""
        return {
            "address": location[0].strip() + ", "+ location[1].strip(),
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
        """Parse or generate links."""
        return links, agenda

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
