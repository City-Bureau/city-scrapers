from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import FormRequest
from scrapy.http.cookies import CookieJar
from datetime import datetime
import re
import scrapelib


class CookElectoralSpider(CityScrapersSpider):
    name = "cook_electoral"
    agency = "Cook County Electoral Board (Suburban Cook)"
    timezone = "America/Chicago"
    start_urls = ["https://aba.cookcountyclerk.com/boardmeetingsearch.aspx"]

    def parse(self, response):
        # years = response.xpath('//select[@id="ddlMeetingYear"]/option/@value').getall()
        self._parse_selected_year(response)

    def _parse_selected_year(self, response):
        selected_year = response.xpath(
            '//select[@id="ddlMeetingYear"]/option[@selected]/@value'
        ).get()
        meeting_ids_this_year = response.xpath(
            '//select[@id="ddlMeetingDate"]/option/@value'
        ).getall()

        jar = CookieJar()
        jar.extract_cookies(response, response.request)

        for meeting_id in meeting_ids_this_year:
            print(f"Fetching: {selected_year} {meeting_id}")
            payload = {
                "ScriptManager1": "UpdatePanel1|btnGo",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__LASTFOCUS": "",
                "__VIEWSTATE": response.xpath(
                    "//input[@id='__VIEWSTATE']/@value"
                ).get(),
                "__VIEWSTATEGENERATOR": response.xpath(
                    "//input[@id='__VIEWSTATEGENERATOR']/@value"
                ).get(),
                "__EVENTVALIDATION": response.xpath(
                    "//input[@id='__EVENTVALIDATION']/@value"
                ).get(),
                "__ASYNCPOST": "true",
                "btnGo.x": "10",
                "btnGo.y": "15",

                "ddlMeetingYear": selected_year,
                "ddlMeetingDate": meeting_id,
            }
            req = FormRequest(
                response.url,
                formdata=payload,
                # Add user-agent to avoid `RESPONSE 179|error|500|The page is performing
                # an async postback but the ScriptManager.SupportsPartialRendering
                # property is set to false. Ensure that the property is set to true during an async postback.`
                headers={"User-Agent": "Mozilla/4.0",},
                callback=self._parse_detail
            )
            # Add cookies to avoid `ERROR 306|error|500|Validation of viewstate MAC failed. If this application
            # is hosted by a Web Farm or cluster, ensure that <machineKey> configuration specifies the
            # same validationKey and validation algorithm. AutoGenerate cannot be used in a cluster`
            jar.add_cookie_header(req)
            yield req

    def _parse_detail(self, response):
        """
        `_parse_detail` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        self._check_errors(response)
        print(response.text)
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

    def _check_errors(self, response):
        if response.url.endswith('Error.aspx'):
            response.status_code = 503
            raise scrapelib.HTTPError(response)

        if not response.text:
            if response.request.method.lower() in {'get', 'post'}:
                response.status_code = 520
                raise scrapelib.HTTPError(response)

        if re.search(r"\|error\|500\|", response.text):
            response.status_code = 500
            raise scrapelib.HTTPError(response)

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        title = "Board Of Commissioners Of Cook County Meeting"
        selected_meeting = response.xpath('//select[@id="ddlMeetingDate"]/option[@selected]/text()').get()
        if selected_meeting.startswith("*"):
           title = "Special " + title
        return title

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        time = item.xpath('//span[@id="lblMeetingTime"]/text()').get()
        am_or_pm = item.xpath('//span[@id="lblDuration"]/text()').get()
        return datetime.strptime(f"{time} {am_or_pm}", "%A, %B %d, %Y %I:%M %p")

    def _parse_location(self, item):
        """Parse or generate location."""
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
        """Parse or generate links."""
        raw_links = item.css('#currentDocDisplay a')
        links = []
        for link in raw_links:
            title = " ".join(link.css("*::text").extract()).strip()
            links.append(
                {"title": title,
                 "href": link.attrib["href"]})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
