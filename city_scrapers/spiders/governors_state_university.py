import re

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime


class GovernorsStateUniversitySpider(CityScrapersSpider):
    name = "governors_state_university"
    agency = "Governors State University"
    timezone = "America/Chicago"
    start_urls = ["https://www.govst.edu/BOT-Meetings/"]
    # used in constructing the links
    base_url = "https://www.govst.edu"
    time_re = r"(?i)([01]?\d)(:?\d*)\s*([ap]\.?m\.?)"


    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for year_section in response.xpath('//div[@class="toggle-list"]/ul/li'):
            year_elt = year_section.xpath('div[@class="title"]/h3/text()')
            year = year_elt.get().replace("Meeting Dates for ", "").strip()
            for row in year_section.xpath('div[@class="content"]/table/tbody/tr'):
                item = row.xpath("td")
                title = self._parse_title(item)
                if title is None:
                    continue
                # if the meeting was postponed, parse_start will return None, and
                # we shouldn't output a meeting.
                start = self._parse_start(item, year)
                if start is None:
                    continue
                meeting = Meeting(
                    title=title,
                    description=self._parse_description(item),
                    classification=self._parse_classification(title),
                    start=start,
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item),
                    links=self._parse_links(item),
                    source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title. The inner html of the first column varies
        quite a bit - brs, divs, b tags - so figuring out what is the title based on
        line position. Sometimes the "title" is only a date, so if all else fails, return
        that.
        Returns None if the title is 'Date', which indicates we're in a header row, or
        empty, which indicates we're in a blank row."""
        cell_text = item[0].css("* ::text").getall()
        clean_cell_text = [elt.strip() for elt in cell_text if len(elt.strip()) > 0]
        if (len(clean_cell_text) == 0) or ("date" in clean_cell_text[0].lower()):
            return None
        if len(clean_cell_text) == 1:
            # then we either have no title or no date - just return whatever we have
            return clean_cell_text[0]
        return " ".join(clean_cell_text[1:])

    def _parse_description(self, item):
        """Parse or generate meeting description. Not available for this website."""
        return ""

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        # if it isn't explicitly described as a committee meeting, then because this
        # is a board calendar, all other meetings are board by default
        return BOARD

    def _normalize_date(self, date, default_year):
        """The dates appear in pretty variable formats, including in some cases without a year.
        This method normalizes."""
        clean_date = date.replace(",", "").replace(".", "").lower().strip()
        # There was a stray "sept." in the data, although usually the month is fully spelled
        # out. Use first three chars of the date string to get the month.
        months = ["january", "february", "march", "april", "may", "june", "july",
                  "august", "september", "october", "november", "december"]
        month_map = {m[:3]: m for m in months}
        month, day, year = re.findall(r"([a-z]+)\.?\s+(\d\d?),?\s*(\d\d\d\d)?", clean_date)[0]
        month = month_map[month[:3]]
        year = year if len(year) == 4 else default_year
        return f"{month} {day} {year}"

    def _normalize_time(self, time_str):
        times = re.findall(self.time_re, time_str)
        if len(times) == 0:
            return None
        hour, minute, ampm = times[0]
        if len(minute.strip(":")) > 0:
            minute = minute.strip(":")
        else:
            minute = "00"
        ampm = ampm.replace(".", "")
        return f"{hour}:{minute} {ampm}"

    def _parse_start(self, item, default_year):
        """Parse start datetime as a naive datetime object. If the meeting was
        postponed or cancelled, return None"""
        # try to find the date in the first column, and if it isn't there, fall back
        # to the third
        day = " ".join(item[0].css("* ::text").getall())
        if not re.search(r"\d", day):
            day = " ".join(item[2].css("* ::text").getall())
        clean_day = self._normalize_date(day, default_year)
        time = " ".join(item[1].css("* ::text").getall()).lower()
        if ("postponed" in time) or ("canceled" in time):
            return None
        clean_time = self._normalize_time(time)
        if clean_time is not None:
            return datetime.strptime(f"{clean_day} {clean_time}", "%B %d %Y %I:%M %p")
        # fall back to midnight if no time specified
        return datetime.strptime(clean_day, "%B %d %Y")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None.
        Not available for this website."""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False. Doesn't seem to occur
        for this website, with the possible exception of the retreats, which aren't quite all day"""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        location = item[1].css("* ::text").getall()
        # remove time if present
        location[0] = re.sub(self.time_re, "", location[0])
        location = [loc.strip() for loc in location if len(loc.strip()) > 0]
        # no obvious way to differentiate location names from addresses other than
        # presence of numbers. We'll assume that the first line is title-only if it
        # contains no numbers, otherwise that it begins the address.
        # If there is no name, just the address, we'll use the first line
        # of the address as the name. If there is no address, use the Governors State
        # University address as the address. If after removing the time there is no
        # information at all, we'll use "Governors State University" as the name
        name = "Governors State University"
        address = "1 University Pkwy,\nUniversity Park, IL 60484"
        if len(location) > 0:
            name = location[0]
        if re.search(r"\d", name):
            address = "\n".join(location)
        elif len(location) > 1:
            address = "\n".join(location[1:])
        # special case for covid -- make sure zoom meetings don't show the university
        # address!
        if ("zoom" in name.lower()) or ("zoom" in address.lower()):
            address = "Zoom"
            name = "Zoom"
        elif "location" in name.lower():
            address = name
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        # the links to the agenda, if present, are in the third and fourth columns
        for col in [2, 3]:
            link_ext = item[col].css("a::attr(href)").get()
            if link_ext is not None:
                link = self.base_url+link_ext
                title = item[col].xpath("a/text()").get()
                links.append({
                    "href": link,
                    "title": title
                })
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
