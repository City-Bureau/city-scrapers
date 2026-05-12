import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiResidentialInvestmentFundSpider(CityScrapersSpider):
    name = "chi_residential_investment_fund"
    agency = "Chicago Residential Investment Fund (RIF)"
    timezone = "America/Chicago"
    start_urls = ["https://www.chicagorif.com/copy-of-about"]

    _location = {
        "name": "City Hall, Rm. 1003A",
        "address": "121 N LaSalle St, Chicago, IL 60610",
    }

    def parse(self, response):
        for item in self._parse_items(response):
            meeting = Meeting(
                title="Board Meeting",
                description="",
                classification=BOARD,
                start=item["start"],
                end=None,
                all_day=False,
                time_notes="",
                location=self._location,
                links=item["links"],
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _get_board_dates_container(self, response):
        """Return the rich text block that contains yearly board dates."""
        selector = "div.wixui-rich-text[data-testid='richTextElement']"
        for container in response.css(selector):
            headings = [
                self._clean_text(text)
                for text in container.css("h5.wixui-rich-text__text::text").getall()
            ]
            if any("Board Dates" in heading for heading in headings):
                return container
        return None

    def _parse_items(self, response):
        """Group meeting dates with any related links from the board dates block."""
        container = self._get_board_dates_container(response)
        if container is None:
            return []

        items = []
        current_item = None

        for el in container.xpath("./h5 | ./p"):
            if el.root.tag == "h5":
                continue

            text = self._clean_text(" ".join(el.css("::text").getall()))
            if not text:
                continue

            parsed_start = self._parse_start_text(text)
            if parsed_start is not None:
                if current_item is not None:
                    items.append(current_item)
                current_item = {
                    "start": parsed_start,
                    "start_text": text,
                    "links": [],
                }
                continue

            if current_item is not None:
                for a in el.css("a[href]"):
                    href = a.attrib.get("href", "").strip()
                    title = self._clean_text(" ".join(a.css("::text").getall())) or href
                    if href:
                        current_item["links"].append({"href": href, "title": title})

        if current_item is not None:
            items.append(current_item)

        return items

    def _parse_start_text(self, text):
        """Parse meeting date text into a naive datetime object."""
        text = self._clean_text(text)
        text = re.sub(r"\bAprli\b", "April", text)

        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None

    def _clean_text(self, text):
        """Normalize text by removing invisible characters and collapsing whitespace."""
        if not text:
            return ""
        text = text.replace("\u200b", "")
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
