import re
from datetime import datetime, timedelta
from io import BytesIO

import requests
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from pdfminer.high_level import extract_text

MONTH_REGEX = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)"
    r"?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)"
    r"?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)

TIME_REGEX = r"(?:[1-9]|1[0-2]):[0-9]{2}\s(?:AM|PM)"


class ChiSouthwestHomeEquityISpider(CityScrapersSpider):
    name = "chi_southwest_home_equity_i"
    agency = "Chicago Southwest Home Equity Commission I"
    timezone = "America/Chicago"
    allowed_domains = ["swhomeequity.com"]
    start_urls = ["https://swhomeequity.com/agenda-%26-minutes"]
    location = {
        "name": "Southwest Home Equity Assurance office",
        "address": "5334 W. 65th Street in Chicago, Illinois",
    }

    def parse(self, response):
        table = response.xpath(
            "body/div/div/div/div[2]/div[3]/div/div/section/div/div[2]"
        )

        for agenda_node in table.xpath(
            "div[@data-ux=\"GridCell\"][contains(., 'Agenda')]"
        ):
            minutes_node = agenda_node.xpath(
                "following-sibling::div[@data-ux=\"GridCell\"][contains(., 'Minutes')]"
            )

            if self._get_link(minutes_node):
                minutes_contents = self.parse_pdf(self._get_link(minutes_node))
            else:
                minutes_contents = None

            meeting = Meeting(
                title=(
                    self._parse_title(minutes_contents)
                    if minutes_contents
                    else "Board Meeting"
                ),
                description="",
                classification=COMMISSION,
                start=self._parse_start(agenda_node),
                end=None,
                all_day=False,
                time_notes=(
                    self._parse_time_notes(minutes_contents)
                    if minutes_contents
                    else None
                ),
                location=self.location,
                links=self._parse_links([agenda_node, minutes_node]),
                source=self._parse_source(response),
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_title(self, text):
        name = re.search(r"Southwest Home Equity Assurance Program", text, flags=re.I)
        minutes = re.search(r"MINUTES", text, flags=re.I)
        if name and minutes:
            title = text[name.end() : minutes.start()]
            return title.replace("\n", "").title().strip()
        else:
            return "Board Meeting"

    def parse_pdf(self, url):
        response = requests.get(url)
        pdf_text = extract_text(BytesIO(response.content))
        return pdf_text

    def _parse_start(self, node):
        # Try to get date from title
        try:
            date_str = self.find_date_in_title(node)
            date_object = datetime.strptime(date_str, "%B %d %Y")
        except (RuntimeError, ValueError):
            try:
                date_str = self.find_date_in_content(node)
                date_object = datetime.strptime(date_str, "%B %d %Y")
            except (RuntimeError, ValueError):
                return None

        try:
            start_time = self.find_time(node)
            return date_object + start_time

        except (RuntimeError, ValueError):
            return date_object + timedelta(hours=18, minutes=30)

    def _parse_links(self, nodes):
        links = []
        for node in nodes:
            if node:
                links.append(
                    {"title": self._get_name(node), "href": self._get_link(node)}
                )
        return links

    def _get_name(self, node):
        name = node.xpath("string(.)").get()
        name = name.replace("(pdf)Download", "")
        return name

    def _get_link(self, node):
        url = node.xpath("a/@href").get()
        if url:
            return "https:" + url
        else:
            return None

    def _parse_source(self, response):
        return response.url

    def find_date_in_title(self, node):
        text = self._get_name(node)
        text_block = text.replace("\n", "")
        return self._use_date_regex(text_block)

    def find_date_in_content(self, node):
        content = self.parse_pdf(self._get_link(node))
        content = content.replace("\n", "")
        return self._use_date_regex(content)

    def find_time(self, node):
        content = self.parse_pdf(self._get_link(node))
        content = content.replace("\n", "")
        time_str = self._use_time_regex(content)
        dt = datetime.strptime(time_str, "%I:%M %p")
        return timedelta(hours=dt.hour, minutes=dt.minute)

    def _use_date_regex(self, text):

        month_ind = re.search(MONTH_REGEX, text, flags=re.I)
        if month_ind is None:
            raise RuntimeError("No month found")
        year_ind = re.search(
            r"\d{4}", text[month_ind.start() :]
        )
        if year_ind is None:
            raise RuntimeError("No year found")
        date_str = text[
            month_ind.start() : (month_ind.start() + year_ind.end())
        ].replace(",", "")
        return date_str

    def _use_time_regex(self, text):

        time_ind = re.search(TIME_REGEX, text, flags=re.I)
        if time_ind is None:
            raise RuntimeError("No time found")
        time_str = text[time_ind.start() : time_ind.end()]
        return time_str

    def _parse_time_notes(self, text):
        c_t_o = re.search(r"CALL TO ORDER", text)
        commissioners = re.search(r"COMMIS(S)?IONER(S)? IN ATTENDANCE", text)
        if c_t_o and commissioners:
            return text[c_t_o.end() : commissioners.start()].replace("\n", "").strip()
        else:
            return None
