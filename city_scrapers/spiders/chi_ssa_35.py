from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

from datetime import datetime, time
from datetime import timedelta
import re


class ChiSsa35Spider(CityScrapersSpider):
    name = "chi_ssa_35"
    agency = "Chicago Special Service Area #35 Lincoln Ave"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.lincolnparkchamber.com/businesses/special-service-areas/lincoln-avenue-ssa/ssa-administration/"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self.title = self._parse_title(response)

        for item in response.css(".content_block p"):
            start = self._parse_start(item)
            if not start:
                continue
            meeting = Meeting(
                start=start,
                title=self.title,
                description='',
                classification=self._parse_classification(item),
                end=self._parse_end(response, start),
                all_day=False,
                # time_notes=self._parse_time_notes(item),
                # location=self._parse_location(item),
                # links=self._parse_links(item),
                # source=self._parse_source(response),
            )

            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        date_str = item.css('*::text').extract_first()
        date_match = re.search('\w{3,9}\s\d{1,2},\s\d{4}', date_str)
        if date_match:
            date_match_str = date_match.group()
            print("FOUND DATE", date_match_str)
            parsed_date = datetime.strptime(date_match_str, '%B %d, %Y')
            return datetime.combine(parsed_date.date(), time(9))

    def _parse_end(self, response, start):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        print('START:', start)
        re_obj = re.compile("typically run (\d+) minutes")
        minutes = re_obj.findall(response.text)[0]
        minutes = int(minutes)
        end = start + timedelta(minutes=minutes)
        return end

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        title = response.css('h5::text').getall()[0]
        # Remove last word
        title_cut = title.rsplit(' ', 1)[0]
        return title_cut

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

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
