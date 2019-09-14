import re
from time import strptime
from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlBoardOfExaminersSpider(CityScrapersSpider):
    name = "il_board_of_examiners"
    agency = "Illinois Board of Examiners"
    timezone = "America/Chicago"
    allowed_domains = ["www.ilboe.org"]
    start_urls = ["https://www.ilboe.org/board-information/board-meetings/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".minutes"):
            meeting = Meeting(
                title="Illinois Board of Examiners - Board Meeting Minutes",
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_str = item.css('.minuteDate::text').get()
        time_str = item.css('.minuteTime::text').get()
        date_ar = date_str.rsplit(" ")
        date = re.sub("\D","",date_ar[1])
        year = re.sub("\D","",date_ar[2])
        month = 13
        in_time = datetime.strptime(time_str, "%I:%M %p")
        out_time = datetime.strftime(in_time, "%H:%M")
        try:
            month = strptime(date_ar[0],'%B').tm_mon
        except:
            month = strptime(date_ar[0],'%b').tm_mon

        temp = year+'-'+str(month)+'-'+date+'T'+out_time+':'+'00'
        datetimeObj = strptime(temp,'%Y-%m-%dT%H:%M:%S')

        return datetimeObj

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        seperator = ","
        [name,address] = seperator.join(item.css(".minutes")[3].css(".minuteLocation").css("p::text").extract()).rsplit("\n",1)
        
        return {
            "name": self.remove_special_chars(name),
            "address": self.remove_special_chars(address),
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        agenda_link = item.css('.minuteAgenda').css('a::attr(href)').get()
        mom_link = item.css('.minuteMinutes').css('a::attr(href)').get()
        if(mom_link):
            return [{"href": agenda_link, "title": "Agenda"},{"href": mom_link, "title": "Minutes"}]
        else:
            return [{"href": agenda_link, "title": "Agenda"}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def remove_special_chars(string_val):
        """Remove all special chars from string"""
        return re.sub(
                r'\s+',
                ' ',
                re.sub(r'(\n)|(--em--)|(--em)|(em--)', ' ', string_val),
                ).strip()
