import re
from datetime import datetime
from zoneinfo import ZoneInfo

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateutil_parser
from dateutil.relativedelta import relativedelta
from scrapy import Selector


class ChiPoliceDistrictCouncilsSpider(CityScrapersSpider):
    name = "chi_police_district_councils"
    agency = "Chicago Police District Councils"
    timezone = "America/Chicago"

    calendar_url = "https://ccpsa.chicago.gov/public-meeting-calendar/"
    calendar_api = "https://ccpsa.chicago.gov/wp-admin/admin-ajax.php"

    DATETIME_RE = re.compile(
        r"(?:[A-Za-z]+,?\s+)?"
        r"([A-Za-z]+\s+\d{1,2},\s*\d{4})"
        r",?\s*(\d{1,2}:\d{2})\s*([ap]m)",
        re.IGNORECASE,
    )

    ADDRESS_RE = re.compile(r"\b[A-Z]{2}\s+\d{5}\b")

    def start_requests(self):
        yield scrapy.Request(
            url=self.calendar_url,
            callback=self._get_initial_meeting_listings,
        )

    def _get_initial_meeting_listings(self, response):
        match = re.search(r'"nonce":"([a-f0-9]+)"', response.text)
        if not match:
            self.logger.error("Could not find nonce on page: %s", response.url)
            return
        nonce = match.group(1)
        now = datetime.now(ZoneInfo(self.timezone)).replace(tzinfo=None)
        start_date = now - relativedelta(years=2)
        end_date = now + relativedelta(months=6)

        while start_date <= end_date:
            formdata = {
                "action": "ccpsa_load_events",
                "nonce": nonce,
                "tab": "all",
                "month": str(start_date.month - 1),
                "year": str(start_date.year),
                "per_page": "50",
                "sort": "desc",
                "context": "all-councils",
                "organizer_id": "0",
            }
            yield scrapy.FormRequest(
                url=self.calendar_api,
                formdata=formdata,
                callback=self.parse,
                cb_kwargs={"formdata": formdata},
            )
            start_date += relativedelta(months=1)

    def _parse_payload(self, response):
        try:
            payload = response.json()
        except ValueError:
            self.logger.error(
                "Non-JSON response (nonce likely expired?): %s", response.url
            )
            return None
        data = payload.get("data")
        if not isinstance(data, dict) or "html" not in data:
            self.logger.error("Unexpected payload structure: %s", payload)
            return None
        if data.get("total", 0) < 1:
            self.logger.debug("Empty month, skipping: %s", response.url)
            return None
        return payload

    def parse(self, response, formdata):
        payload = self._parse_payload(response)
        if not payload:
            return
        yield from self._paginate(payload, formdata)

        rows = Selector(text=payload["data"]["html"]).css(
            "tr.event-row:not(.no-events-row)"
        )
        for row in rows:
            yield from self._parse_row(row, response)

    def _paginate(self, payload, formdata):
        total_pages = payload["data"].get("total_pages", 1)
        current_page = int(formdata.get("page", 1))
        if current_page < total_pages:
            next_formdata = formdata.copy()
            next_formdata["page"] = str(current_page + 1)
            yield scrapy.FormRequest(
                self.calendar_api,
                formdata=next_formdata,
                callback=self.parse,
                cb_kwargs={"formdata": next_formdata},
            )

    def _parse_row(self, row, response):
        detail_href = row.css("td.event-meeting a::attr(href)").get()
        attachment_href = row.css("td.event-files.files-column a::attr(href)").get()
        datetime_str = self.DATETIME_RE.search(
            row.css("td:nth-child(3)").xpath("string()").get() or ""
        )

        if attachment_href or not datetime_str:
            if not detail_href:
                self.logger.warning("No detail page URL for: %s", response.url)
                return
            yield scrapy.Request(
                detail_href,
                callback=self._parse_meeting_details,
                cb_kwargs={"row": row},
            )
            return

        try:
            dt_object = dateutil_parser(datetime_str.group(0))
        except (ValueError, TypeError) as e:
            self.logger.error(
                "Could not parse listing datetime %r on %s: %s",
                datetime_str.group(0),
                response.url,
                e,
            )
            return
        yield self._build_meeting(row, {"start": dt_object, "source": detail_href})

    def _parse_meeting_details(self, response, row):
        dt_str = (
            response.xpath("//p[normalize-space()='Date']/following-sibling::p[1]")
            .xpath("string()")
            .get()
        )

        try:
            dt_object = dateutil_parser(dt_str)
        except (ValueError, TypeError) as e:
            self.logger.error(
                "Could not parse datetime %r from detail page %s: %s",
                dt_str,
                response.url,
                e,
            )
            return

        overrides = {
            "start": dt_object,
            "links": self._parse_links(response),
            "source": response.url,
        }

        yield self._build_meeting(row, overrides)

    def _build_meeting(self, row, overrides=None):
        row_text = "".join(row.css("td::text").getall()).strip()
        location, note = self._parse_location_text(row)
        meeting = Meeting(
            title=self._parse_title(row),
            description="",
            classification=COMMISSION,
            end=None,
            all_day=False,
            time_notes=note,
            location=location,
            links=[],
        )
        if overrides:
            meeting.update(overrides)
        meeting["status"] = self._get_status(meeting, text=row_text)
        meeting["id"] = self._get_id(meeting)
        return meeting

    def _parse_title(self, row):
        title_str = row.css("::attr(data-organizer)").get() or ""
        return title_str.strip()

    def _parse_location_text(self, row):
        loc_text = row.css("td:nth-child(4)").xpath("string()").get() or ""
        collapsed = re.sub(r"\s+", " ", loc_text).strip().rstrip("-").strip()
        collapsed = re.sub(r"^UPDATED:\s*", "", collapsed, flags=re.IGNORECASE).strip()

        if re.search(r"United States", collapsed, flags=re.IGNORECASE):
            collapsed = re.sub(
                r",?\s+United States", "", collapsed, flags=re.IGNORECASE
            ).strip()
            name, sep, address = collapsed.partition(" - ")
            if sep and not re.match(r"^\d", name):
                return {
                    "name": name.strip(),
                    "address": address.strip(),
                }, ""
            return {
                "name": "",
                "address": collapsed.replace(" - ", ", ").strip(),
            }, ""

        return {
            "address": "",
            "name": "",
        }, collapsed or ""

    def _parse_links(self, response):
        links = []
        video_href = response.css("a.video-link::attr(href)").get()
        if video_href:
            links.append({"title": "Video", "href": video_href})

        docs_table = response.css("table.event-documents-table.table tr")
        if docs_table:
            for row in docs_table:
                link_title = row.css("td.file-name::text").get()
                link_href = row.css("a.preview-link::attr(href)").get()
                if link_title and link_href:
                    links.append({"title": link_title.strip(), "href": link_href})

        return links
