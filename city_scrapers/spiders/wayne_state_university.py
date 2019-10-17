from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import re

class WayneStateUniversitySpider(CityScrapersSpider):
    name = "wayne_state_university"
    agency = "Wayne State University"
    timezone = "America/Chicago"
    allowed_domains = ["http://bog.wayne.edu"]
    start_urls = ["http://bog.wayne.edu/"]
    location = {
            "name": "McGregor Memorial Conference Center", 
            "address": "Room BC 495 Gilmour Mall, Detroit, MI 48202",
        }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        self._validate_location(response)
        for item in response.xpath('//*[@id="content"]/div[1]/div/h2').re('((?:January|Feburary|March|April|May|June|July|August|October|September|November|December)\s+\d{1,2},\s+\d{4})'):
            meetings = self._parse_meeting_types(response)
            for meeting_type in meetings: 
                meeting = Meeting(
                    title = meeting_type[0],
                    description=self._parse_description(item),
                    classification= meeting_type[-1], 
                    start= meeting_type[1],
                    end= "Ending Time Not Specified",
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self.location,
                    links=self._parse_links(item,response),
                    source=self._parse_source(response),
                )
                yield meeting
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

            

    def _parse_meeting_types(self, response):
        """ Parse meeting titles and start times. Returns a list of tuples including titles and meeting times """
        meeting_details = []
        meeting_types = []
        for item in response.css('#content .border-t li').extract(): #interate through meeting times and types
            start_time = re.search('(\d+:\d{1,2}\s(?:a.m|p.m))', item)
            title = re.search('(\d+:\d{1,2}\s(?:a.m.|p.m.)\s-\s)(.+)$', item)
            if ("Board" not in item or "board" not in item):
                meeting_classification = COMMITTEE
            else:
                meeting_classification = BOARD
            meeting_types.append([title,start_time,meeting_classification])
        return meeting_types
    
    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "See source to confirm details. Times may change"

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False 

    def _validate_location(self,response):
        if "Room BC" not in response.xpath('//*[@id="content"]/div[1]/div/p[1]'):
            raise ValueError("The location has changed! Please check source!")

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = {}
        href = response.xpath('//*[@id="content"]/div[2]').re('\/meetings\/\d{4}\/\d{2}-\d{2}').pop()
        title = item + " Meeting"
        links.update({href: title})
        if len(response.css('#content .lg\:flex li a').extract()) > 0: #scape meeting notes
            next_page = "http://bog.wayne.edu/" + href 
            documents = re.search('//*[@id="content"]/div[2]/ul', next_page)
            for items in documents:
                title = documents.xpath('//a/text').pop()
                href = documents.xpath('//a/@href').pop()
                links.update({href: title})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return "http://bog.wayne.edu/"