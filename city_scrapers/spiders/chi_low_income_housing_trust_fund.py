import re
from datetime import date, datetime

import pytz
from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from icalendar import Calendar


class ChiLowIncomeHousingTrustFundSpider(CityScrapersSpider):
    name = "chi_low_income_housing_trust_fund"
    agency = "Chicago Low-Income Housing Trust Fund"
    timezone = "America/Chicago"
    start_urls = ["https://clihtf.org/?post_type=tribe_events&ical=1&eventDisplay=list"]

    def parse(self, response):
        """
        Parse the .ics file and handle data irregularities.
        """
        cleaned_content = self.clean_ics_data(response.text)
        try:
            cal = Calendar.from_ical(cleaned_content)
        except Exception as e:
            self.logger.error("Error parsing iCalendar data: %s", e)
            self.logger.error(
                "Response content: %s", response.text[:500]
            )  # Log first 500 chars
            raise

        for component in cal.walk():
            # This agency has many 'Administrative Day' events that
            # are not actual meetings
            if (
                component.name == "VEVENT"
                and "Administrative Day" not in component.get("summary")
            ):
                meeting = Meeting(
                    title=component.get("summary").strip(),
                    description=component.get("description", "").strip() or "",
                    classification=self._parse_classification(component.get("summary")),
                    start=self._to_naive(component.get("dtstart").dt),
                    end=self._to_naive(component.get("dtend").dt),
                    all_day=self._is_all_day(
                        component.get("dtstart").dt, component.get("dtend").dt
                    ),
                    time_notes="",
                    location=self._parse_location(component),
                    links=[
                        {
                            "href": component.get("url", "").strip(),
                            "title": "Event Details",
                        }
                    ],
                    source=response.url,
                )
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def clean_ics_data(self, ics_content):
        """Handles a quirk in the ICS file where VTIMEZONE blocks are formatted
        improperly and cause icalendar parsing errors."""
        normalized_content = ics_content.replace("\r\n", "\n")
        cleaned_content = re.sub(
            r"BEGIN:VTIMEZONE.*?END:VTIMEZONE\n",
            "",
            normalized_content,
            flags=re.DOTALL,
        )
        return cleaned_content

    def _parse_classification(self, title):
        if "committee" in title.lower():
            return COMMITTEE
        elif "board" in title.lower():
            return BOARD
        return NOT_CLASSIFIED

    def _to_naive(self, dt):
        """Convert timezone-aware datetime to naive datetime in the local timezone,
        or return the date object if it's a date."""
        print("dt: ", dt)
        local_timezone = pytz.timezone(
            self.timezone
        )  # Ensure you are using the spider's timezone
        if isinstance(dt, datetime):
            if dt.tzinfo is not None:
                return dt.astimezone(local_timezone).replace(tzinfo=None)
            return dt
        elif isinstance(dt, date):
            # Convert date to datetime for uniform handling
            return datetime.combine(dt, datetime.min.time(), tzinfo=None)
        return dt

    def _is_all_day(self, start, end):
        """Check if the event is an all-day event."""
        return type(start) is date and (end - start).days == 1

    def _parse_location(self, component):
        """Parse or generate location."""
        location = component.get("location", "")
        if not location:
            return {
                "name": "Chicago Low-Income Housing Trust Fund",
                "address": "77 West Washington Street, Suite 719, Chicago, IL 60602",
            }
        return {"name": location, "address": ""}
