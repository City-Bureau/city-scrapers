import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import scrapy
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    COMMITTEE,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil import parser
from dateutil.tz import gettz


class IlCriminalJusticeInformationSpider(CityScrapersSpider):
    name = "il_criminal_justice_information"
    agency = "Illinois Criminal Justice Information Authority"
    timezone = "America/Chicago"
    attachments_base_url = "https://agency.icjia-api.cloud"
    meetings_base_url = "https://icjia.illinois.gov/news/meetings/"
    custom_settings = {"ROBOTSTXT_OBEY": False}
    default_location = {"name": "TBD", "address": ""}
    online_keywords = (
        r"webex|zoom|teams|virtual|teleconference|online|video|conference|webinar"
    )

    def start_requests(self):
        """
        Request agency's GraphQL endpoint to get all meetings.
        """
        query = """
        query allMeetings {
            meetings(sort: "start:desc") {
                id
                title
                slug
                summary
                created_at
                updated_at
                published_at
                isCancelled
                start
                end
                category
                body
                posts {
                    title
                    slug
                    __typename
                }
                events {
                    title: name
                    slug
                    __typename
                }
                tags {
                    title
                    slug
                    __typename
                }
                attachments {
                    id
                    formats
                    size
                    name
                    ext
                    url
                    updated_at
                    created_at
                    hash
                    __typename
                }
                external {
                    title
                    url
                    __typename
                }
                __typename
            }
        }
        """

        # Prepare the payload
        payload = {"operationName": "allMeetings", "variables": {}, "query": query}

        # Convert the payload to a JSON string
        body = json.dumps(payload)

        # Send the POST request
        yield scrapy.Request(
            "https://agency.icjia-api.cloud/graphql",
            method="POST",
            body=body,
            headers={"Content-Type": "application/json"},
            callback=self.parse,
        )

    def parse(self, response):
        data = json.loads(response.text)
        # save to tests dir

        for item in data["data"]["meetings"]:
            title = item["title"]
            title_with_status = f"{title} (Cancelled)" if item["isCancelled"] else title
            start = self.parse_datetime(item["start"])
            # skip meetings older than 90 days
            ninety_days_ago = datetime.now() - timedelta(days=90)
            if start < ninety_days_ago:
                continue
            description, location = self._parse_description_and_location(item)
            meeting = Meeting(
                title=title_with_status,
                description=description,
                classification=self._parse_classification(item["title"]),
                start=start,
                end=self.parse_datetime(item["end"]),
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(item),
                source=self._parse_source(item),
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def parse_datetime(self, dt_str):
        """
        Parse ISO string into datetime, convert to local timezone,
        then create timezone naive datetime object.
        """
        if not dt_str:
            return None
        dt = parser.parse(dt_str)
        local_tz = gettz(self.timezone)
        local_dt = dt.astimezone(local_tz)
        naive_dt = local_dt.replace(tzinfo=None)
        return naive_dt

    def _parse_classification(self, title):
        """
        Classifies the meeting based on keywords in the meeting title.
        If no keywords match (e.g. task forces), defaults to COMMISSION.
        """
        title = title.lower()
        # "advisory" is checked first, because advisory committees also contain
        # the word "committee"
        if "advisory" in title:
            return ADVISORY_COMMITTEE
        if "committee" in title:
            return COMMITTEE
        if "board" in title:
            return BOARD
        return COMMISSION

    def _parse_description_and_location(self, meeting):
        """
        Parse the description and location from the meeting text, which holds both.
        The API has the text in both "summary" and "body", but either one can be
        cut short, so the longer one is used.
        Online meetings keep the default location and get their meeting link added
        to the description. If several locations are listed, the first one is used
        as the location, and the description keeps all of them.
        """
        texts = sorted(
            [
                self._clean_text(meeting["summary"]),
                self._clean_text(meeting.get("body")),
            ],
            key=len,
            reverse=True,
        )
        description = texts[0]
        if re.search(self.online_keywords, description, re.I):
            link = self._parse_online_link(meeting)
            if link and link not in description:
                description = f"{description}\n\nMeeting link: {link}"
        location = (
            self._parse_location(texts[0])
            or self._parse_location(texts[1])
            or dict(self.default_location)
        )
        return description, location

    def _clean_text(self, text):
        """
        Remove markdown bold markers and surrounding whitespace.
        """
        return (text or "").replace("**", "").strip()

    def _parse_online_link(self, meeting):
        """
        Find the online meeting link. It's usually only in the body, not the summary.
        """
        text = f"{meeting['summary'] or ''}\n{meeting.get('body') or ''}"
        match = re.search(r"https?://\S*(?:webex|zoom|teams)\S*", text, re.I)
        return match.group(0) if match else None

    def _parse_location(self, text):
        """
        Find the first in-person location in the meeting text. Returns None if there
        isn't one, e.g. for online-only meetings.
        """
        # Numbered list: "Two Locations:\n\n1.  Building\nStreet\nCity ..."
        numbered = re.search(
            r"^\s*1\.\s+(.+?)(?=\n\s*\n|\n\s*2\.|\Z)", text, re.M | re.S
        )
        if numbered:
            return self._build_location(numbered.group(1))
        # City lines: "Chicago: Building, Street"
        city_line = re.search(r"^\s*(Chicago|Springfield):\s*(.+)$", text, re.M)
        if city_line:
            city, value = city_line.groups()
            location = self._build_location(value)
            location["address"] = f"{location['address']}, {city}, IL"
            return location
        # Single line: "Location: Building, Street, City" (not an online location)
        location_line = re.search(r"Location:?[ \t]*([^\n]+)", text, re.I)
        if location_line:
            value = location_line.group(1)
            if re.search(r"\d", value) and not re.search(
                self.online_keywords, value, re.I
            ):
                return self._build_location(value)
        return None

    def _build_location(self, text):
        """
        Split location text into name and address. The first part is the name,
        unless it starts with a number, in which case it's all address.
        """
        parts = [part.strip() for part in re.split(r"[,\n]", text) if part.strip()]
        if parts[0][0].isdigit():
            return {"name": "", "address": ", ".join(parts)}
        return {"name": parts[0], "address": ", ".join(parts[1:])}

    def _parse_source(self, meeting):
        """
        Build the meeting's page URL on the agency website from its slug field.
        """
        return urljoin(self.meetings_base_url, f"{meeting['slug']}/")

    def _parse_links(self, meeting):
        # Extracting links from attachments and external
        links = []
        attachments = meeting.get("attachments", [])
        for attachment in attachments:
            links.append(
                {
                    "href": urljoin(self.attachments_base_url, attachment["url"]),
                    "title": self._parse_link_title(attachment["name"]),
                }
            )
        external = meeting.get("external", {})
        if external:
            links.append({"href": external["url"], "title": external["title"]})
        return links

    def _parse_link_title(self, name):
        """
        Clean up an attachment file name.
        """
        title = re.sub(r"\.\w+$", "", name)
        title = title.replace("_", " ")
        title = re.sub(
            r"[\s-]*(\d{6}|\d{8}|\d{1,2}[.-]\d{1,2}[.-]\d{2,4})\s*$", "", title
        )
        return re.sub(r"\s+", " ", title).strip()
