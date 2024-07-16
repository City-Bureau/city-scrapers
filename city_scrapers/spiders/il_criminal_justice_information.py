import json
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
            meeting = Meeting(
                title=title_with_status,
                description=item["summary"],
                classification=self._parse_classification(item["title"]),
                start=start,
                end=self.parse_datetime(item["end"]),
                all_day=False,
                time_notes="",
                location={
                    "name": "TBD",
                    "address": "",
                },
                links=self._parse_links(item),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def parse_datetime(self, dt_str):
        """
        Parse ISO string into datetime, convert to local timezone,
        then create timezone naive datetime object.
        """
        dt = parser.parse(dt_str)
        local_tz = gettz(self.timezone)
        local_dt = dt.astimezone(local_tz)
        naive_dt = local_dt.replace(tzinfo=None)
        return naive_dt

    def _parse_classification(self, title):
        """
        Classifies the meeting based on the meeting title.
        If no specific keywords match, defaults to COMMISSION.
        """
        category_map = {
            "Board": BOARD,
            "Committee": COMMITTEE,
            "Advisory Committee": ADVISORY_COMMITTEE,
        }
        return category_map.get(title, COMMISSION)

    def _parse_links(self, meeting):
        # Extracting links from attachments and external
        links = []
        attachments = meeting.get("attachments", [])
        for attachment in attachments:
            links.append(
                {
                    "href": urljoin(self.attachments_base_url, attachment["url"]),
                    "title": attachment["name"],
                }
            )
        external = meeting.get("external", {})
        if external:
            links.append({"href": external["url"], "title": external["title"]})
        return links
