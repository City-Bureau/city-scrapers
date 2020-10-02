import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlGovernorsStateUniversitySpider(CityScrapersSpider):
    name = "il_governors_state_university"
    agency = "Governors State University"
    timezone = "America/Chicago"
    start_urls = ["https://www.govst.edu/BOT-Meetings/"]
    time_re = r"(?i)([01]?\d)(:?\d*)\s*([ap]\.?m\.?)"

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        for year_section in response.xpath('//div[@class="toggle-list"]/ul/li'):
            year_elt = year_section.xpath('div[@class="title"]/h3/text()')
            # sometimes the year is not present in the table dates, so grab it from the
            # section heading as backup
            year = year_elt.get().replace("Meeting Dates for ", "").strip()
            for row in year_section.xpath('div[@class="content"]/table/tbody/tr'):
                item = row.xpath("td")
                title = self._parse_title(item)
                if title is None:
                    continue
                meeting = Meeting(
                    title=title,
                    description=self._parse_description(item),
                    classification=self._parse_classification(title),
                    start=self._parse_start(item, year),
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item),
                    links=self._parse_links(item, response),
                    source=self._parse_source(response),
                )

                # if postponed or canceled appears in any of these columns, it means the
                # meeting is canceled, so just pass in all the row text to _get_status
                row_text = " ".join(row.css("* ::text").getall())
                meeting["status"] = self._get_status(meeting, text=row_text)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _clean_igsu_title(self, title):
        """Reformat title to conform to project naming standards"""
        if not title.startswith("Special"):
            return re.sub(r"\s*Meeting\s*$", "", title)
        return title

    def _parse_title(self, item):
        """Parse or generate meeting title. The inner html of the first column varies
        quite a bit - brs, divs, b tags - so figuring out what is the title based on
        line position. Sometimes the "title" is only a date, so if all else fails,
        return that.
        Returns None if the title is 'Date', which indicates we're in a header row, or
        if the title is empty, which indicates we're in a blank row.
        If returning a string, strip 'Meeting' from the end."""
        cell_text = item[0].css("* ::text").getall()
        clean_cell_text = [elt.strip() for elt in cell_text if len(elt.strip()) > 0]
        if (len(clean_cell_text) == 0) or ("date" == clean_cell_text[0].lower()):
            return None
        if len(clean_cell_text) == 1:
            # then we either have no title or no date - or, occasionally, we have a
            # comma-separated title and date. First check for \d\d\d\d under the
            # assumption that this ends the date, and see if the remainder of the
            # string is non-empty. Failing that, check if there are numbers,
            # and if so assume it's a date and return Board of Trustees. Otherwise,
            # return the line, assuming the whole thing is the title.
            possible_title = clean_cell_text[0]
            title_match = re.findall(r"\d\d\d\d\s+(.*)", possible_title)
            if len(title_match) > 0:
                return self._clean_igsu_title(title_match[0])
            if re.search(r"\d", clean_cell_text[0]):
                return "Board of Trustees"
            return self._clean_igsu_title(clean_cell_text[0])
        return self._clean_igsu_title(" ".join(clean_cell_text[1:]))

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
        # There was a stray "sept." in the data, although usually the month is
        # fully spelled out. Use first three chars of the date string to get the month.
        months = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        month_map = {m[:3]: m for m in months}
        month, day, year = re.findall(
            r"([a-z]+)\.?\s+(\d\d?),?\s*(\d\d\d\d)?", clean_date
        )[0]
        month = month_map[month[:3]]
        year = year if len(year) == 4 else default_year
        return f"{month} {day} {year}"

    def _normalize_time(self, time_str):
        """Normalize time format. Sometimes it comes with colons or periods,
        sometimes not"""
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
        """Parse start datetime as a naive datetime object."""

        # try to find the date in the first column, and if it isn't there, fall back
        # to the third
        day = " ".join(item[0].css("* ::text").getall())
        if not re.search(r"\d", day):
            day = " ".join(item[2].css("* ::text").getall())
        clean_day = self._normalize_date(day, default_year)
        time = " ".join(item[1].css("* ::text").getall()).lower()
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
        for this website, with the possible exception of the retreats, which aren't
        quite all day"""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        unclean_location_cell_content = item[1].css("* ::text").getall()
        # remove time if present, and clean
        location_cell_content = []
        for line in unclean_location_cell_content:
            line = re.sub(self.time_re, "", line)
            line = line.strip().strip("-").strip()
            if len(line) > 0:
                location_cell_content.append(line)
        # It's not obvious whether the first line of the location_cell_content
        # is a location name or address, so the rest of this method uses heuristics
        # for this
        default_name = "Governors State University"
        default_address = "1 University Pkwy,\nUniversity Park, IL 60484"
        name, address = default_name, default_address
        # If the event was postponed or canceled, we will handle that in the
        # event status, and can just use the defaults here
        for elt in location_cell_content:
            if ("postponed" in elt.lower()) or ("canceled" in elt.lower()):
                return {"address": default_address, "name": default_name}
        # If there is no name, just the address, we'll use the first line
        # of the address as the name.
        if len(location_cell_content) > 0:
            name = location_cell_content[0]
        # no obvious way to differentiate location names from addresses other than
        # presence of numbers. We'll assume that the first line is title-only if it
        # contains no numbers, otherwise that it begins the address.
        if re.search(r"\d", name):
            address = "\n".join(location_cell_content)
        elif len(location_cell_content) > 1:
            address = "\n".join(location_cell_content[1:])
        # Room may end up in either the name or address; if it's present, we want to
        # make sure it's part of the address. Sometimes room numbers appear without
        # room, as a single word (see G330 in 2017) so handle them the same way
        if "room " in address.lower():
            address = address + "\n" + default_address
        if "room " in name.lower():
            if "room " not in address.lower():
                address = name + "\n" + address
            name = default_name
        # special case for covid -- make sure zoom meetings don't show the university
        # address!
        if ("zoom" in name.lower()) or ("zoom" in address.lower()):
            address = "Zoom"
            name = "Zoom"
        elif "location tbd" in name.lower():
            address = name
        # in some cases a one-word "address" like G330 in 2017 can make it through,
        # so fall back to the default here as well
        elif len(address.split()) == 1:
            address = address + "\n" + default_address
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        # the links to the agenda, if present, are in the third and fourth columns
        for col in [2, 3]:
            for link_parent in item[col].xpath("a"):
                link_ext = link_parent.css("::attr(href)").get()
                if link_ext is not None:
                    link = response.urljoin(link_ext)
                    title = link_parent.xpath("text()").get()
                    links.append({"href": link, "title": title})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
