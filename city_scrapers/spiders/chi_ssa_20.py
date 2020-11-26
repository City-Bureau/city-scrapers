from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import re
from datetime import datetime
import w3lib.html as w3


class ChiSsa20Spider(CityScrapersSpider):
    name = "chi_ssa_20"
    agency = "Chicago Special Service Area #20 South Western Avenue"
    timezone = "America/Chicago"
    start_urls = ["https://www.mpbhba.org/business-resources/"]

    def parse(self, response):

        #debug
        #print('\n','!!!begin!!!')

        base = response.xpath(
               "//*[self::p or self::strong or self::h3]/text()").getall()

        # remove whitespaces, convert all to lowercase
        base = [ re.sub(r"\s+", " ", item).lower() for item in base ]

        # remove lines from our section backward 
        # "ssa meetings" is where our interest begins
        for index, line in enumerate(base):
            if 'ssa meetings' in line:
                del base[:index]

        # remove lines from our section onward
        # in this case, "ssa 64" and following entries
        # we don't care for. 
        for index, line in enumerate(base):
            if 'ssa 64' in line:
                del base[index:]

        
        for item in base: 
            # don't hand off empty lines to methods
            if re.match(r'^\s*$', item):
                continue
            
            print('now passing', item)

            meeting = Meeting(
#              title=self._parse_title(entry),
#              description=self._parse_description(entry),
#              classification=self._parse_classification(entry),
               start=self._parse_start(item),
#              end=self._parse_end(entry),
#              all_day=self._parse_all_day(entry),
#              time_notes=self._parse_time_notes(entry),
#              location=self._parse_location(entry),
#              links=self._parse_links(entry),
#              source=self._parse_source(response),
            )
#
#           meeting["status"] = self._get_status(meeting)
#           meeting["id"] = self._get_id(meeting)
#
#           yield meeting

        # debug
        #print('!!!end!!!', '\n')


    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
  
         # Year:
         # catches the line '2019 ssa meetings' as it's the only
         # one with four digits starting it, then extracts those
         # four digits with re.match() to provide us with a date
         # string we can work with.
         if re.match('^\D*\d{4}\D*$', item):
             year = re.match('^\d{4}', item)[0]

         # Date:
         # we only care for lines containing the dates,
         # e.g "wednesday, june 5, 9 a.m."
         # 'beverly' will remove lines containing the location
         # 'ssa' will remove other lines we don't need
         if not any(word in item for word in ['beverly', 'ssa']):

                # remove commas and dots in order to nicely format for
                # strptime(), the strip() is for final whitespace removal
                # if no strip(), strptime() will reject the string as not
                # formatted sufficiently
                item = re.sub(r'([,\.])', '', item).strip()
                date_object=datetime.strptime(item, "%A %B %d %I %p")
                print(type(date_object))

#            try:
#                print('attempting', item)
#                item = re.sub(r'([,\.])', '', item)
#                date_object=datetime.strptime(item, "%A %B %d %I %p")
#                print('!!!!!!!!!!!!')
#                print(type(date_object))
#            except ValueError:
#                print('passed due to valueError')
#                pass

#        return None

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
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
