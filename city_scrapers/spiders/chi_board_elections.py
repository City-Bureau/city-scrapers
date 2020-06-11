import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiBoardElectionsSpider(CityScrapersSpider):
    name = "chi_board_elections"
    agency = "Chicago Board of Elections"
    timezone = "America/Chicago"
    start_urls = [
        "https://app.chicagoelections.com/pages/en/board-meetings.aspx",
        "https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx",
    ]
    location = {
        "address": "8th Floor Office, 69 W. Washington St. Chicago, IL 60602",
        "name": "Cook County Administration Building",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if (
            "minutes" in response.url
        ):  # Current meetings and past meetings on differerent pages
            yield from self._prev_meetings(response)
        else:
            yield from self._next_meeting(response)

    def _next_meeting(self, response):
        text = response.xpath("//text()").extract()
        # Will return full dates, like "9:30 a.m. on Dec. 11, 2018"
        date_strs = [
            re.search(r"\d{1,2}:.*20\d{2}", x).group(0)
            for x in text
            if re.search(r"\d{1,2}:.*20\d{2}", x)
        ]
        # Has meeting location
        body_text = response.xpath('//div[@class="copy"]/text()').extract()
        # Check for 69 (in 69 W Washington) in any of the strings, raise error if not
        # present and location may have changed
        if not any("69" in text for text in body_text):
            raise ValueError("The meeting address may have changed")

        for date_str in date_strs:
            start = self._parse_start(date_str, "")
            meeting = Meeting(
                title="Electoral Board",
                description="",
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes="Meeting end time is estimated",
                all_day=False,
                location=self.location,
                links=self._parse_links(response, start=start),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _prev_meetings(self, response):
        """
        Meetingdate regex first searches for the 3 types of hyphens that
        chi_board_elections uses (they like switching it up), and then finds a year
        number, and returns everything in between.
        """

        items = response.xpath("//a|//span/text()").extract()
        prev_start = None
        six_months_ago = datetime.now() - timedelta(days=180)
        for item in items:
            next_idx = items.index(item) + 1
            item = item.replace("\xa0", " ")  # Gets rid of non-breaking space character
            try:
                item_date = re.search(r"(–|- |-)(.+[0-9]{4})", item).group(2)
                while len(item_date) > 30:
                    item_date = re.search(r"(–|- |-)(.+[0-9]{4})", item_date).group(2)
                item_date.lstrip()
                start = self._parse_start(item_date, item)
                if start < six_months_ago and not self.settings.getbool(
                    "CITY_SCRAPERS_ARCHIVE"
                ):
                    continue
                if prev_start != start:  # To acount for duplicates
                    meeting = Meeting(
                        title="Electoral Board",
                        description="",
                        classification=COMMISSION,
                        start=start,
                        end=None,
                        time_notes="Meeting end time is estimated",
                        all_day=False,
                        location=self.location,
                        links=self._parse_links(response, meeting=item),
                        source=response.url,
                    )
                    # In case there's both minutes and video for one date
                    if next_idx < len(items):
                        next_item = items[next_idx].replace("\xa0", " ")
                        next_date = re.search(r"(–|- |-)(.+[0-9]{4})", next_item).group(
                            2
                        )
                        while len(next_date) > 30:
                            next_date = re.search(
                                r"(–|- |-)(.+[0-9]{4})", next_date
                            ).group(2)
                        next_date.lstrip()
                        next_start = self._parse_start(next_date, next_item)
                        if next_start == meeting["start"] and "href" in next_item:
                            meeting["links"].extend(
                                self._parse_links(response, next_item)
                            )
                    meeting["status"] = self._get_status(meeting)
                    meeting["id"] = self._get_id(meeting)
                    yield meeting
                prev_start = start
            except AttributeError:  # Sometimes meetings will return None
                continue

    def _parse_start(self, date_str, meeting_text):
        """Parse start datetime"""
        date_str = date_str.replace("\xa0", " ")
        if len(date_str.split(", ")) > 2:
            date_str = ", ".join(date_str.split(", ")[1:])
        time_str = "9:30 AM"
        if "7 " in meeting_text:
            time_str = re.search(r"7\s+[apmAPM\.]{2,4}", meeting_text).group(0)
            time_str = time_str.replace("7 ", "7:00 ")
        if ":" not in date_str or meeting_text:
            dt_str = "{} on {}".format(time_str, date_str)
        else:
            dt_str = date_str
        dt_str = (
            dt_str.replace(".", "")
            .replace("am", "AM")
            .replace("pm", "PM")
            .replace("Sept", "Sep")
        )
        try:
            dt = datetime.strptime(dt_str, "%I:%M %p on %b %d, %Y")
        except ValueError:  # Some months are abbreviated, some are not
            dt = datetime.strptime(dt_str, "%I:%M %p on %B %d, %Y")
        return dt

    def _parse_links(self, response, meeting=None, start=None):
        """Parse agendas and minutes"""
        if meeting is None:
            for link in response.css("a"):
                if "genda" in link.css("*::text").extract_first():
                    agenda_href = response.urljoin(link.attrib["href"])
                    if start:
                        agenda_href = "{}?date={}".format(
                            agenda_href, start.strftime("%Y%m%d")
                        )
                    return [{"href": agenda_href, "title": "Agenda"}]
        elif "href" not in meeting:
            return []
        if "minutes" in response.url:
            if "Minutes" in meeting:
                minutes_link = re.search(r'"\/.+"', meeting).group(0).strip('"')
                return [
                    {
                        "href": "https://app.chicagoelections.com{}".format(
                            minutes_link
                        ),
                        "title": "Minutes",
                    }
                ]
            elif "youtu" in meeting:
                videolink = re.search(r'"h.+"', meeting).group(0).strip('"')
                return [{"href": videolink, "title": "Video"}]
        return []
