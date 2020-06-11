from datetime import datetime, time, timedelta

from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    FORUM,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa62Spider(CityScrapersSpider):
    name = "chi_ssa_62"
    agency = "Chicago Special Service Area #62 Sauganash"
    timezone = "America/Chicago"
    start_urls = ["http://escc60646.com/our_events/?date1=all"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        for item in response.xpath('//li[@class="event "]'):
            times = self._parse_times(item)
            if times[0] is None or (datetime.now() - times[0]) > timedelta(days=90):
                continue
            title = self._parse_title(item)
            classification = self._parse_classification(item)
            if title and classification is not NOT_CLASSIFIED:
                meeting = Meeting(
                    title=title,
                    description=self._parse_description(item),
                    classification=classification,
                    start=times[0],
                    end=times[1],
                    all_day=False,
                    time_notes="",
                    location=self._parse_location(item),
                    links=self._parse_links(item),
                    source=self._parse_source(item),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    @staticmethod
    def _parse_title(item):
        """Parse or generate meeting title."""
        title = item.xpath(".//div[@class='event-title']/h3/a/text()").get()
        if title:
            title = title.replace("SSA #62", "").strip()
        return title

    @staticmethod
    def _parse_description(item):
        """Parse or generate meeting description."""
        return item.xpath(
            "string(.//div[@class='event-content']/p[not(descendant::a)])"
        ).get()

    @staticmethod
    def _parse_classification(item):
        """Parse or generate classification from allowed options."""
        title = item.xpath(".//div[@class='event-title']/h3/a/text()").get()
        if title:
            if "board" in title.lower():
                return BOARD
            elif "advisory" in title.lower() or "commission" in title.lower():
                return ADVISORY_COMMITTEE
            elif "forum" in title.lower():
                return FORUM
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_times(item):
        """Parse start and end datetimes as a naive datetime object."""
        month = item.xpath('.//div[@class="event-month"]/text()').get().strip()
        day = item.xpath('.//div[@class="event-day"]/text()').get().strip()
        year = item.xpath('.//div[@class="event-year"]/text()').get().strip()
        ddate = datetime.strptime("%s %s %s" % (month, day, year), "%b %d %Y").date()

        time_str = item.xpath('.//span[@class="event-time"]/text()').get()
        if time_str is None:
            return None, None
        times = time_str.strip().replace(".", "")
        if not ("a" in times or "p" in times) or "cancel" in times.lower():
            return datetime.combine(ddate, time()), None
        ttimes = times.split("-")
        ampm = ttimes[0].split(" ")[1]
        starttime = datetime.strptime(ttimes[0].strip(), "%I:%M %p").time()
        start = datetime.combine(ddate, starttime)
        if len(ttimes) > 1:
            if not ("a" in ttimes[1] or "p" in ttimes[1]):
                ttimes[1] = ttimes[1] + " " + ampm
            endtime = datetime.strptime(ttimes[1].strip(), "%I:%M %p").time()
            end = datetime.combine(ddate, endtime)
        else:
            end = None

        return start, end

    @staticmethod
    def _parse_location(item):
        """Parse or generate location."""
        location = item.xpath('.//span[@class="event-location"]/text()').get().strip()
        location_split = location.split(",")
        if len(location_split) == 1 or any(char.isdigit() for char in location[0]):
            name = ""
            address = location.strip()
        else:
            name = location_split[0].strip()
            address = ", ".join(x.strip() for x in location_split[1:])
        address += ", Chicago, IL"
        return {"name": name, "address": address}

    @staticmethod
    def _parse_links(item):
        """Parse or generate links."""
        title = item.xpath(".//div[@class='event-content']/p/a/text()").get()
        href = item.xpath(".//div[@class='event-content']/p/a/@href").get()
        if title is None:
            return []
        return [{"href": href, "title": title}]

    @staticmethod
    def _parse_source(item):
        """Parse or generate source."""
        return item.xpath(".//div[@class='event-title']/h3/a/@href").get()
