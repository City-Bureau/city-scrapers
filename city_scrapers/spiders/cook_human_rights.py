import re
from collections import defaultdict
from datetime import datetime, timedelta

import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class CookHumanRightsSpider(CityScrapersSpider):
    name = "cook_human_rights"
    agency = "Cook County Human Rights"
    timezone = "America/Chicago"
    start_urls = ["https://www.cookcountyil.gov/agency/commission-human-rights-0"]

    def __init__(self, *args, **kwargs):
        self.link_map = defaultdict(list)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        """
        links = response.css(
            "#block-fieldblock-node-agency-default-field-resources .content a"
        )
        pattern = r"( *)(?P<m>[a-zA-Z]+)( *)(\d+),( *)(?P<y>\d{4})"
        for link in links:
            link_text = " ".join(link.css("*::text").extract()).strip()
            link_relative_path = link.attrib["href"]  # href = reletive file address
            file_id = re.search(r"\d{4,6}", link_relative_path)
            url = "https://www.cookcountyil.gov/file/{}/".format(file_id[0])

            if "Minutes" in link_text:
                regex = re.search(pattern, link_text)
                if regex is not None:
                    raw_monthyear = regex.group("m") + " " + regex.group("y")
                    if len(regex.group("m")) < 4:
                        date_obj = datetime.strptime(raw_monthyear, "%b %Y")
                    else:
                        date_obj = datetime.strptime(raw_monthyear, "%B %Y")
                    formatted_date = datetime.strftime(date_obj, "%y-%m")
                    yield response.follow(
                        url=url,
                        method="GET",
                        callback=self._parse_meetings_page,
                        meta={"formatted_date": formatted_date},
                    )

    def _parse_links(self, response):
        """Parse file page to get minutes file link"""
        formatted_date = response.meta.get("formatted_date")
        link = response.xpath("//a[contains(@href, 'default/files')]")
        link_path = link.xpath("./@href").extract_first()
        self.link_map[formatted_date].append({"title": "Minutes", "href": link_path})

    def _parse_meetings_page(self, response):
        """
        Triger collecting Minutes' files
        Go to calendar page for extract mettings
        """
        self._parse_links(response)
        today = datetime.now()
        for month_delta in range(-6, 6):  # Meetings from 6 month ago to next 6 month
            mo_str = (today + relativedelta(months=month_delta)).strftime("%Y-%m")
            url = (
                "https://www.cookcountyil.gov/"
                "calendar-node-field-date/month/{}".format(mo_str)
            )
            yield scrapy.Request(
                url=url, method="GET", callback=self._parse_events_page
            )

    def _parse_events_page(self, response):
        """ parse the calendar page to find human rights  commitee meetings """
        for url in self._get_event_urls(response):
            yield scrapy.Request(url, callback=self._parse_event, dont_filter=True)

    def _get_event_urls(self, response):
        """
        Get urls for all Human rights Commission meetings on the page
        """
        responses = []
        events = response.xpath("//a[contains(@href, 'event')]")
        for event in events:
            event_title = event.xpath("text()").extract_first().lower()
            if "human rights" in event_title:
                href = event.xpath("./@href").extract_first()
                responses.append(response.urljoin(href))
        return responses

    def _parse_event(self, response):
        """Parse the event page."""
        start = self._parse_start(response)
        links_key = start.strftime("%y-%m")

        meeting = Meeting(
            title=self._parse_title(),
            description=self._parse_description(response),
            classification=self._parse_classification(),
            start=start,
            end=self._parse_end(response),
            time_notes=self._parse_time_notes(),
            all_day=self._parse_all_day(response),
            location=self._parse_location(response),
            links=self.link_map[links_key],
            source=response.url,
        )

        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)

        return meeting

    def _parse_title(self):
        """Parse or generate meeting title."""
        return "Commission on Human Rights"

    def _parse_description(self, response):
        """Parse or generate meeting description."""
        block = response.xpath(
            "//div[contains(@class,'field-name-field-event-description')]"
        )
        field_items = block.xpath(".//div[contains(@class, 'field-items')]")
        return " ".join(
            field_items.xpath(".//p/text()").extract()
            + field_items.xpath(".//strong/text()").extract()
        ).strip()

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, response):
        """Parse start date and time"""
        start = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        start = "".join(start).upper()
        start = start.split(" TO ")[0].strip()
        start = start.replace("(ALL DAY)", "12:00AM")

        return datetime.strptime(start, "%B %d, %Y %I:%M%p")

    def _parse_end(self, response):
        """Parse end date and time"""
        date = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        date = "".join(date).upper()
        date.replace("(ALL DAY)", " TO 11:59PM")
        start_end = date.split(" TO ")

        if len(start_end) < 2:
            start = datetime.strptime(start_end[0], "%B %d, %Y %I:%M%p")
            return start + timedelta(hours=2)  # usually this meeting takes 2 hours

        end_time = start_end[1]
        date = start_end[0][: start_end[0].rindex(" ")]
        return datetime.strptime("{} {}".format(date, end_time), "%B %d, %Y %I:%M%p")

    def _parse_time_notes(self):
        """Parse any additional notes on the timing of the meeting"""
        return "Regular meetings are held on the second Thursday of every other month"

    def _parse_all_day(self, response):
        """
        Parse or generate all-day status. Defaults to false.
        """
        date = response.xpath(
            '//span[@class="date-display-single"]/descendant-or-self::*/text()'
        ).extract()
        date = "".join(date).upper()
        return "ALL DAY" in date

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        address = response.xpath(
            '//div[@class="field event-location"]/descendant::*/text()'
        ).extract()
        for word in ["Location:", ", ", " "]:
            address.remove(word)
        address = " ".join(address)
        if "Virtual Meeting" in address:
            return {
                "address": "",
                "name": "Virtual Meeting",
            }
        else:
            return {
                "address": address,
                "name": "",
            }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
