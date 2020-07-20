import re
from datetime import datetime

import scrapelib
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import FormRequest
from scrapy.http.cookies import CookieJar


class CookElectoralSpider(CityScrapersSpider):
    name = "cook_electoral"
    agency = "Cook County Electoral Board (Suburban Cook)"
    timezone = "America/Chicago"
    start_urls = ["https://aba.cookcountyclerk.com/boardmeetingsearch.aspx"]

    def parse(self, response):
        available_years = response.xpath(
            '//select[@id="ddlMeetingYear"]/option/@value'
        ).getall()

        year, meeting_ids = self._find_year_and_meetings(response)
        self.cookie_jar = CookieJar()
        self.cookie_jar.extract_cookies(response, response.request)

        # Parse the current year without re-fetching, since we already have it
        for m in self._parse_meetings_in_year(response):
            yield m

        today = datetime.now().today()
        next_year = str(today.year + 1)
        last_year = str(today.year - 1)

        # Fetch surrounding years if appropriate.
        # We need a valid meeting ID from _any_ year for this to work
        if next_year in available_years:
            yield self._build_request(
                response, next_year, meeting_ids[0], parse_all=True
            )

        # If we're still near the start of the year, fetch last year for any updates
        if today.month < 2:
            yield self._build_request(
                response, last_year, meeting_ids[0], parse_all=True
            )

    def _find_year_and_meetings(self, response):
        selected_year = response.xpath(
            '//select[@id="ddlMeetingYear"]/option[@selected]/@value'
        ).get()
        meeting_ids_this_year = response.xpath(
            '//select[@id="ddlMeetingDate"]/option/@value'
        ).getall()
        return selected_year, meeting_ids_this_year

    def _hidden_field_value(self, response, fieldname):
        value_as_input = response.xpath(f"//input[@id='{fieldname}']/@value").get()
        if value_as_input:
            return value_as_input
        # Beyond the initial response, hidden fields are returned in non-HTML format
        exp = re.compile(f"hiddenField\|{fieldname}\|(.*?)\|")  # noqa
        regex_value = re.search(exp, response.text)
        if regex_value:
            return regex_value.group(1)

    def _build_request(self, response, year, meeting_id, parse_all=False):
        payload = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": self._hidden_field_value(response, "__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": self._hidden_field_value(
                response, "__VIEWSTATEGENERATOR"
            ),
            "__EVENTVALIDATION": self._hidden_field_value(
                response, "__EVENTVALIDATION"
            ),
            "__ASYNCPOST": "true",
            "ScriptManager1": "UpdatePanel1|btnGo",
            "btnGo.x": "10",
            "btnGo.y": "15",
            "ddlMeetingYear": year,
            "ddlMeetingDate": meeting_id,
        }
        callback = self._parse_meeting
        if parse_all:
            callback = self._parse_meetings_in_year

        req = FormRequest(
            response.url,
            formdata=payload,
            # Add user-agent to avoid `RESPONSE 179|error|500|The page is performing
            # an async postback but the ScriptManager.SupportsPartialRendering
            # property is set to false.
            # Ensure that the property is set to true during an async postback.`
            headers={"User-Agent": "Mozilla/4.0"},
            callback=callback,
        )

        # Add cookies to avoid `ERROR 306|error|500|Validation of viewstate MAC failed.
        # If this application is hosted by a Web Farm or cluster, ensure that
        # <machineKey> configuration specifies the same validationKey and validation
        # algorithm. AutoGenerate cannot be used in a cluster`
        self.cookie_jar.add_cookie_header(req)
        return req

    def _check_errors(self, response):
        if response.url.endswith("Error.aspx"):
            response.status_code = 503
            raise scrapelib.HTTPError(response)

        if not response.text:
            if response.request.method.lower() in {"get", "post"}:
                response.status_code = 520
                raise scrapelib.HTTPError(response)

        if re.search(r"\|error\|500\|", response.text):
            response.status_code = 500
            raise scrapelib.HTTPError(response)

    def _parse_meetings_in_year(self, response):
        selected_year, meeting_ids = self._find_year_and_meetings(response)

        for meeting_id in meeting_ids:
            yield self._build_request(response, selected_year, meeting_id)

    def _parse_meeting(self, response):
        self._check_errors(response)
        meeting = Meeting(
            title=self._parse_title(response),
            description="",
            classification=BOARD,
            start=self._parse_start(response),
            end=None,
            all_day=False,
            time_notes=None,
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=self._parse_source(response),
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, response):
        title = "Board Of Commissioners Of Cook County Meeting"
        selected_meeting = response.xpath(
            '//select[@id="ddlMeetingDate"]/option[@selected]/text()'
        ).get()
        if selected_meeting.startswith("*"):
            title = "Special " + title
        return title

    def _parse_start(self, item):
        time = item.xpath('//span[@id="lblMeetingTime"]/text()').get()
        am_or_pm = item.xpath('//span[@id="lblDuration"]/text()').get()
        return datetime.strptime(f"{time} {am_or_pm}", "%A, %B %d, %Y %I:%M %p")

    def _parse_location(self, item):
        name = item.xpath('//span[@id="lblLocation"]/text()').get()
        street = item.xpath('//span[@id="lblAddress"]/text()').get()
        city = item.xpath('//span[@id="lblCity"]/text()').get()
        state = "IL"
        address = f"{street}, {city} {state}"
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        raw_links = item.css("#currentDocDisplay a")
        links = []
        for link in raw_links:
            title = " ".join(link.css("*::text").extract()).strip()
            links.append({"title": title, "href": link.attrib["href"]})
        return links

    def _parse_source(self, response):
        return response.url
