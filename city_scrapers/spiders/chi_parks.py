import re
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from city_scrapers_core.constants import BOARD, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class ChiParksSpider(LegistarSpider):
    name = "chi_parks"
    agency = "Chicago Park District"
    timezone = "America/Chicago"
    tzinfo = ZoneInfo(timezone)
    start_urls = ["https://chicagoparkdistrict.legistar.com/Calendar.aspx"]
    # A street address ending in "Chicago, IL <zip>", with the place name before it
    address_re = re.compile(
        r"(?P<name>.*?)\s*(?P<street>\d+\s[^,]+?),?\s+Chicago,?\s+IL,?\s+(?P<zip>\d{5})"
    )
    # Leading all-caps meeting labels, e.g. "REGULAR BOARD MEETING", "(VIRTUAL)"
    label_re = re.compile(r"^(?:[A-Z]+\b|\([A-Z]+\))(?:\s+(?:[A-Z]+\b|\([A-Z]+\)))*\s*")
    # Signs that a meeting is held online, e.g. "(VIRTUAL)" or a Teams link
    virtual_re = re.compile(r"\b(?:virtual|online|teams|zoom|webex)\b|https?://", re.I)
    # Abbreviated street directions, e.g. "4830 S. Western Avenue"
    direction_re = re.compile(r"\b([NSEW])\.\s")
    directions = {"N": "North", "S": "South", "E": "East", "W": "West"}
    # The site names its headquarters several ways, e.g. "Administration Building"
    admin_building_re = re.compile(
        r"^(?:Chicago Park District )?Administration Building(?: \(Park \d+\))?$"
    )
    admin_building = "Chicago Park District Administration Building"

    def parse_legistar(self, events):
        if not events:
            self.logger.warning("No Legistar events to parse")
        # Skip meetings more than 1 year old unless the archive setting is enabled.
        twelve_months = datetime.now(self.tzinfo).replace(tzinfo=None) - timedelta(
            days=365
        )
        for event in events:
            start, time_notes = self._parse_start(event)
            if not start or (
                start < twelve_months
                and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
            ):
                continue

            location_text = self._parse_location_text(event)
            meeting = Meeting(
                title=self._parse_title(event),
                description=self._parse_description(event, location_text),
                classification=self._parse_classification(event),
                start=start,
                end=None,
                all_day=False,
                time_notes=time_notes,
                location=self._parse_location(location_text),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )
            # "RESCHEDULED" labels the new date of a meeting that was held, so it
            # must not count as a cancellation
            meeting["status"] = self._get_status(
                meeting, text=location_text.lower().replace("rescheduled", "")
            )

            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_legistar_events(self, response):
        """
        Replaces the core parser, which drops every row on this site. The calendar
        icon column has a blank header whose hidden input holds a single space, so
        the core never labels it "iCalendar", then skips each row for having no
        iCalendar URL. Here the column is recognized by its link, and a row without
        one is kept rather than dropped.
        """

        events_tables = response.css("table.rgMasterTable")
        if not events_tables:
            self.logger.warning("No Legistar events table found on %s", response.url)
            return []
        events_table = events_tables[0]

        headers = []
        for header in events_table.css("th[class^='rgHeader']"):
            header_text = " ".join(header.css("*::text").getall()).strip()
            header_inputs = [
                value.strip() for value in header.css("input::attr(value)").getall()
            ]
            header_alts = header.css("img::attr(alt)").getall()
            headers.append(
                header_text
                or next(filter(None, header_inputs), "")
                or next(iter(header_alts), "")
            )
        events = []
        for row in events_table.css("tr.rgRow, tr.rgAltRow"):
            try:
                data = {}
                for header, field in zip(headers, row.css("td")):
                    field_text = " ".join(
                        " ".join(field.css("*::text").getall()).split()
                    )
                    url = None
                    link = field.css("a")
                    if link:
                        attrs = link.attrib
                        if "href" in attrs:
                            url = response.urljoin(attrs["href"])
                        # Some Legistar links open a popup instead, as the core allows
                        elif attrs.get("onclick", "").startswith(
                            ("radopen('", "window.open", "OpenTelerikWindow")
                        ):
                            url = response.urljoin(attrs["onclick"].split("'")[1])
                    if url and "View.ashx?M=IC" in url:
                        data["iCalendar"] = {"url": url}
                    elif url:
                        data[header] = {"label": field_text, "url": url}
                    else:
                        data[header] = field_text
                events.append(data)
            except Exception:
                self.logger.exception(
                    "Failed to parse Legistar row %r on %s", row, response.url
                )
        return events

    def _parse_start(self, item):
        """
        Parse the start datetime and its time notes. The core helper drops a row
        with no time and crashes on a bad date, so a missing or unreadable time
        falls back to midnight with a note, and an unreadable date skips the row.
        """
        date_str = (item.get("Meeting Date") or "").strip()
        time_str = (item.get("Meeting Time") or "").strip()
        try:
            date = datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            self.logger.warning("Skipping meeting with unreadable date %r", date_str)
            return None, None
        try:
            start_time = datetime.strptime(time_str, "%I:%M %p").time()
        except ValueError:
            self.logger.warning(
                "Unreadable time %r on %s, using midnight", time_str, date_str
            )
            return (
                datetime.combine(date, time()),
                "Please check the meeting attachment for start time details.",
            )
        return datetime.combine(date, start_time), "Estimated 2 hour duration"

    def _parse_location_text(self, item):
        """Get the Meeting Location cell's text."""
        loc_item = item.get("Meeting Location") or ""
        if isinstance(loc_item, dict):
            return loc_item.get("label", "")
        return loc_item

    def _parse_location(self, location_text):
        """
        Split the location cell into a place name and street address. The cell
        starts with a meeting label like "REGULAR BOARD MEETING", which is dropped,
        and may end with notes after the ZIP code, which are ignored.
        """
        match = self.address_re.search(location_text)
        if match:
            name = self.label_re.sub("", match.group("name")).strip()
            if self.admin_building_re.match(name):
                name = self.admin_building
            street = self.direction_re.sub(
                lambda m: f"{self.directions[m.group(1)]} ", match.group("street")
            ).strip()
            return {
                "name": name or "TBD",
                "address": f"{street}, Chicago, IL {match.group('zip')}",
            }
        if self.virtual_re.search(location_text):
            return {"name": "Virtual", "address": ""}
        return {"name": "TBD", "address": ""}

    def _parse_description(self, item, location_text):
        """
        Describe how to join an online meeting. When the location cell shows a
        virtual meeting, its text after the labels and any street address (e.g.
        "Microsoft Teams Meeting link: https://...") becomes the description.
        """
        if not self.virtual_re.search(location_text):
            return ""
        match = self.address_re.search(location_text)
        text = location_text[match.end() :] if match else location_text
        description = self.label_re.sub("", text.strip()).strip()
        loc_item = item.get("Meeting Location")
        url = loc_item.get("url") if isinstance(loc_item, dict) else None
        if url and url not in description:
            description = f"{description} {url}".strip()
        return description

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        board_str = "Board of Commissioners"
        if item["Name"].strip() == board_str:
            return board_str
        return "{}: {}".format(board_str, item["Name"])

    def _parse_classification(self, item):
        """
        Differentiate board meetings from public hearings and forums.
        """
        name = item["Name"].lower()
        if "hearing" in name or "forum" in name:
            return FORUM
        return BOARD
