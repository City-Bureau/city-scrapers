import re
from datetime import datetime, timedelta, time
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
        "address": "5334 W 65th St Chicago, IL 60638",
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

            meeting = Meeting(
                title="Governing Commission",
                description="",
                classification=COMMISSION,
                start=self._parse_start(agenda_node),
                end=None,
                all_day=False,
                time_notes="See links for details",
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
        date_str = self.find_date_in_title(node)
        if date_str is not None:
            date_obj = self._convert_date_str(date_str)
            print(date_obj)
            return date_obj
        else:
            return None

    def _convert_date_str(self, date_str):
        try:
            date_object = datetime.strptime(date_str, "%B %d %Y")
        # If we only have the month and year
        except ValueError:
            try:
                date_object = datetime.strptime(date_str, "%B %Y")
            except ValueError:
                # If that doesn't work, return None
                return None
        return datetime.combine(date_object, time(18, 30, 0))

    def find_date_in_title(self, node):
        text = node.xpath("string(.)").get()
        text_block = text.replace("\n", "")
        return self._use_date_regex(text_block)

    def _use_date_regex(self, text):

        month_ind = re.search(MONTH_REGEX, text, flags=re.I)
        if month_ind is None:
            return None
        year_ind = re.search(r"\d{4}", text[month_ind.start() :])
        if year_ind is None:
            return None
        date_str = text[
            month_ind.start() : (month_ind.start() + year_ind.end())
        ].replace(",", "")
        return date_str

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
        if name.lower().find("minutes") > -1:
            return "Minutes"
        elif name.lower().find("agenda") > -1:
            return "Agenda"
        else:
            return None

    def _get_link(self, node):
        url = node.xpath("a/@href").get()
        if url and url.startswith("http"):
            return url
        # Unusual format but many links on this website
        # unfortunately begin this way
        elif url and url.startswith("//"):
            return "https:" + url
        elif url:
            return "https://" + url
        else:
            return None

    def _parse_source(self, response):
        return response.url
