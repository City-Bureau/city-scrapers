from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import scrapy
import datetime
import re

month_mapping = {
    "January"  : 1,
    "February" : 2,
    "March"    : 3,
    "April"    : 4,
    "May"      : 5,
    "June"     : 6,
    "July"     : 7,
    "August"   : 8,
    "September": 9,
    "October"  : 10,
    "November" : 11,
    "December" : 12,
}


class ChiNorthernIlUniversitySpider(CityScrapersSpider):
    name = "chi_northern_il_university"
    agency = "Northeastern Illinois University"
    timezone = "America/Chicago"
    start_urls = ["https://www.neiu.edu/about/board-of-trustees/calendar-of-meetings"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.material_map = dict()

    def parse(self, response):
        #print(response)
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs. 
        """
        #print(response)

        self._parse_links()
        yield None
        '''
        items_list = response.xpath('//div[@class="field field--name-field-generic-body field--type-text-long field--label-hidden field--item"]')
        year_list = items_list.xpath('.//h2')
        for years in year_list.extract():
            #print(years)
            year = re.findall('\d{4}',years)[0]
            items = year_list.xpath('.//following-sibling::ul[1]/li').extract()
            for item in items:
                #print(item)
                meeting = Meeting(
                    title=self._parse_title(item),
                    description='',
                    classification=self._parse_classification(item),
                    start=self._parse_start(item,year),
                    end=None,
                    #all_day=self._parse_all_day(item),
                    time_notes="See agenda for meeting time",
                    location=self._parse_location(item),
                    #links=self._parse_links(item),
                    #source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting'''

    def _parse_title(self, item):

        """Parse or generate meeting title."""
        pattern= re.compile('-(.*(Committee|Meeting))',re.IGNORECASE)
        title_list = re.findall(pattern, item)
        #print(title_list)
        if title_list == None:
            return 'Board of Trustees'
        title, ign=title_list[-1]
        #print(title)
        return title.replace("<strong>","").replace("</strong>","").replace("\xa0"," ")

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if 'committee' in title.lower():
            return COMMITTEE
        if "meeting" in title.lower():
            return BOARD
        return NOT_CLASSIFIED

    def _parse_start(self, item,year):
        """Parse start datetime as a naive datetime object."""
        pattern = re.compile('([a-z]+)(,|\u00a0|\u0020)+([a-z]+)(,|\u00a0|\u0020)+([0-9]{1,2})',re.IGNORECASE)
        day, ign1, month, ign2, date = re.findall(pattern,item)[0]
        date_obj = datetime.datetime(int(year),month_mapping[month],int(date),13,00)
        return date_obj

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_location(self, item):
        """Parse or generate location."""
        if "**" in item:
            return {
                "address": "",
                "name": "Jacob H. Carruthers Center",
        }
        if "*" in item:
            return {
                "address": "",
                'name'   : "El Centro"
            }

        return {
            "address": "5500 North St. Louis Avenue, Chicago, Ill., 60625",
            "name"   : 'Northeastern Illinois University'
        }

    def _parse_links(self):
        """Parse or generate links."""

        link_response = scrapy.Request("https://www.neiu.edu/about/board-of-trustees/board-meeting-materials")
        material_list = link_response.xpath('//div[@class="field field--name-field-generic-body field--type-text-long field--label-hidden field--item"]/h3')
        
        print(material_list)

        url_infos = ''
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
