import re
from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa20Spider(CityScrapersSpider):
    name = "chi_ssa_20"
    agency = "Chicago Special Service Area #20 South Western Avenue"
    timezone = "America/Chicago"
    start_urls = ["https://www.mpbhba.org/business-resources/"]
    location = {
        "name": "Beverly Bank & Trust,",
        "address": "10258 s. Western ave.",
    }

    def parse(self, response):

        base = response.xpath(
            "//*[self::p or self::strong or self::h3]/text()").getall()

        # remove whitespaces, convert all to lowercase
        base = [re.sub(r"\s+", " ", item).lower() for item in base]

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
            print('now passing', item)

            # don't pass empty lines to methods
            if re.match(r'^\s*$', item):
                continue

            start = self._parse_start(item)
            if not start:
                continue

            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=start,
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self.location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "SSA 20"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):

        # Year:
        # Catches the line '2019 ssa meetings' as it's the only
        # one with four digits starting it, then extracts those
        # four digits with re.match() to provide us with a date
        # integer we can work with.
        if re.match(r'^\D*\d{4}\D*$', item):
            year = re.match(r'^\d{4}', item)[0]

        # Date:
        # Now, We only care for lines containing the dates,
        # e.g "wednesday, june 5, 9 a.m."
        # 'beverly' will remove lines containing the location
        # 'ssa' will remove other lines we don't need
        if not any(word in item for word in ['beverly', 'ssa']):

            # Remove commas and dots in order to nicely format for
            # strptime()
            # strip() is for final whitespace removal
            # if no strip(), strptime() will reject the string as not
            # formatted sufficiently
            # Finally, concat date and year strings and pass to strptime()
            year = year
            item = re.sub(r'([,\.])', '', item).strip()
            ready_date = item + ' ' + str(self.year)
            date_object = datetime.strptime(ready_date, "%A %B %d %I %p %Y")
            return(date_object)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url