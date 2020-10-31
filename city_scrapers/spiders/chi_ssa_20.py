from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa20Spider(CityScrapersSpider):
    name = "chi_ssa_20"
    agency = "Chicago Special Service Area #20 South Western Avenue"
    timezone = "America/Chicago"
    start_urls = ["https://www.mpbhba.org/business-resources/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        response_items = response.xpath("//*[contains(@class, 'et_pb_text_inner')]")
        full_h3 = response.xpath('//h3')
        print(full_h3)

#        for item, key in enumerate(response_items):
#            print("item is %s and key is %s" %(item, key))
            
        #h3_xpath = response_items.xpath("//*[contains(@h3, 'SSA Meetings')]")
        h3_xpath = response_items.xpath('//h3')
        #print(h3_xpath)



            #h3_xpath = key.xpath('@h3').get()
#            meeting = Meeting(
#                title=self._parse_title(item),
#                description=self._parse_description(item),
#                classification=self._parse_classification(item),
#
#                start=self._parse_start(item),
#
#                end=self._parse_end(item),
#                all_day=self._parse_all_day(item),
#                time_notes=self._parse_time_notes(item),
#                location=self._parse_location(item),
#                links=self._parse_links(item),
#                source=self._parse_source(response),
#            )
#
#            meeting["status"] = self._get_status(meeting)
#            meeting["id"] = self._get_id(meeting)

#            yield meeting

#    def _parse_title(self, item):
#        """Parse or generate meeting title."""
#        return ""
#
#    def _parse_description(self, item):
#        """Parse or generate meeting description."""
#        return ""
#
#    def _parse_classification(self, item):
#        """Parse or generate classification from allowed options."""
#        return NOT_CLASSIFIED
#
#    def _parse_start(self, item):
#        """Parse start datetime as a naive datetime object."""
#        return None
#
#        return None
#
#    def _parse_end(self, item):
#        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
#        return None
#
#    def _parse_time_notes(self, item):
#        """Parse any additional notes on the timing of the meeting"""
#        return ""
#
#    def _parse_all_day(self, item):
#        """Parse or generate all-day status. Defaults to False."""
#        return False
#
#    def _parse_location(self, item):
#        """Parse or generate location."""
#        return {
#            "address": "",
#            "name": "",
#        }
#
#    def _parse_links(self, item):
#        """Parse or generate links."""
#        return [{"href": "", "title": ""}]
#
#    def _parse_source(self, response):
#        """Parse or generate source."""
#        return response.url
