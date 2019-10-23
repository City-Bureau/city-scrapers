import re
from dateutil.parser import parse

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthRiverMentalHealthSpider(CityScrapersSpider):
    name = "chi_north_river_mental_health"
    agency = "North River Expanded Mental Health Services Program and Governing Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www.northriverexpandedmentalhealthservicescommission.org"]
    start_urls = ["http://www.northriverexpandedmentalhealthservicescommission.org/minutes.html"]


    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".meetings"):
            meeting = Meeting(
                title="Governing Commission",   
                description='',
                classification="COMMISSION",
                start="7 pm",
                end=None,
                all_day=False,
                time_notes='',
                location={
                    "name": "North River Expanded Mental Health Services Program Governing Commission Office",
                    "address": "3525 W. Peterson Ave, Unit 306, Chicago, IL 60659",
                },
                links=self._parse_links(response),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting
    

    def _parse_links(self, response, doc_date, doc_url):
        """Parse or generate links."""  
        doc_list = [] 
        doc_list.append({ 
            "date": doc_date, 
            "href": doc_url
                     })  
        return doc_list


    def _parse_past_minutes(self, response):
        """Parse or generate links."""  
        for doc in response.css('div.paragraph a[href*="uploads"]'): 
            doc_link = doc.attrib['href'] 
            doc_url = response.urljoin(doc_link)
            return doc_url


    def _parse_calendar(self, response):
        """Parse or generate links."""  
        for date_link in response.css('div.paragraph a[href*="uploads"]').re("[A-Za-z]{3,9}(?:._|_)\d\d(?:._|_|_\w\w_)\d\d\d\d|[01]\d\d\d\d\d"): 
            meeting_date = date_link.replace(".",'').replace("_",' ').replace("2c",'') 
            date = parse(meeting_date)
            doc_date = date.strftime('%m-%d-%Y') 
            return doc_date 
            

