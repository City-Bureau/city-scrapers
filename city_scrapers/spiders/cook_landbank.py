import json
import re
from collections import defaultdict
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookLandbankSpider(CityScrapersSpider):
    name = "cook_landbank"
    agency = "Cook County Land Bank Authority"
    timezone = "America/Chicago"
    start_urls = [
        "http://www.cookcountylandbank.org/",
        "http://www.cookcountylandbank.org/agendas-minutes/",
    ]
    location = {
        "name": "Cook County Administration Building",
        "address": "69 W Washington St Chicago, IL 60602",
    }

    def __init__(self, *args, **kwargs):
        self.documents_map = defaultdict(list)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        if response.url == self.start_urls[0]:
            yield from self._parse_home(response)
        else:
            self._parse_documents_page(response)
            dates_to_scrape = set([d for _, d in self.documents_map.keys()])
            for date_obj in dates_to_scrape:
                yield scrapy.FormRequest(
                    url="http://www.cookcountylandbank.org/wp-admin/admin-ajax.php",
                    formdata={
                        "action": "the_ajax_hook",
                        "current_month": date_obj.strftime("%m"),
                        "current_year": str(date_obj.year),
                        "fc_focus_day": date_obj.strftime("%d"),
                        "direction": "none",
                    },
                    callback=self._parse_form_response,
                )

    def _parse_home(self, response):
        for item in response.css(".evosl_slider > .event"):
            yield from self._parse_detail(item)

    def _parse_documents_page(self, response):
        for section in response.css(".panel-group"):
            title = section.css(".fusion-toggle-heading::text").extract_first().strip()
            title_key = self._parse_title_key(title)
            sections_split = section.css(".panel-body").extract()[0].split("<hr>")
            # Parse the most recent three meetings
            for meeting_section in sections_split[:3]:
                item = scrapy.Selector(text=meeting_section)
                date_str = re.sub(
                    r"((?<=\d)[a-z]+|,)",
                    "",
                    " ".join(item.css("h2 *::text").extract()).strip(),
                )
                if not date_str:
                    continue
                date_obj = datetime.strptime(date_str, "%B %d %Y").date()
                for doc_link in item.css("a"):
                    doc_title = (
                        " ".join(doc_link.css("*::text").extract()).strip().title()
                    )
                    self.documents_map[(title_key, date_obj)].append(
                        {
                            "title": doc_title,
                            "href": response.urljoin(doc_link.attrib["href"]),
                        }
                    )

    def _parse_form_response(self, response):
        """Parse detail links for parsing from form response"""
        data = json.loads(response.text)
        content = scrapy.Selector(text=data["content"])
        for meeting_link in content.css("a[itemprop='url']"):
            yield response.follow(
                meeting_link.attrib["href"],
                callback=self._parse_detail,
                dont_filter=True,
            )

    def _parse_detail(self, sel):
        """Parse detail page selector or response"""
        title_str = sel.css("[itemprop='name']::text").extract_first().strip()
        # Avoid scraping the contest
        if "win" in title_str.lower():
            return
        start = self._parse_start(sel)
        meeting = Meeting(
            title=self._parse_title(title_str),
            description="",
            classification=self._parse_classification(title_str),
            start=start,
            end=None,
            time_notes="",
            all_day=False,
            location=self._parse_location(sel),
            links=self._parse_links(sel, title_str, start),
            source=self._parse_source(sel),
        )

        meeting["status"] = self._get_status(meeting, text=title_str)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, title_str):
        return re.split(r" (?=CCLBA)", title_str)[-1].replace(" Meeting", "").strip()

    def _parse_title_key(self, title):
        """Get a title key to match documents and meetings"""
        if "board" in title.lower():
            return "board"
        else:
            return re.search(r"(?<=CCLBA)\s+\w+", title).group().strip().lower()

    def _parse_start(self, item):
        start_str = item.css("[itemprop='startDate']::attr(content)").extract_first()
        return datetime.strptime(start_str, "%Y-%m-%dT%H:%M")

    def _parse_classification(self, name):
        if "board" in name.lower():
            return BOARD
        return COMMITTEE

    def _parse_location(self, item):
        item_sel = item.css("[itemprop='location']")
        loc = {**self.location}
        loc_name = item_sel.css("[itemprop='name']::text").extract_first()
        loc_addr = item_sel.css("[itemprop='streetAddress']::text").extract_first()
        if loc_name and loc_name.strip():
            loc["name"] = loc_name.strip()
        if loc_addr and loc_addr.strip() and "69 W" not in loc_addr:
            loc_addr = loc_addr.strip()
            if "Chicago" not in loc_addr:
                loc_addr += " Chicago, IL"
            loc["address"] = loc_addr
        return loc

    def _parse_links(self, item, title, start):
        title_key = self._parse_title_key(title)
        links = self.documents_map[(title_key, start.date())]
        for doc_link in item.css(".eventon_full_description a"):
            doc_title = " ".join(doc_link.css("*::text").extract()).strip()
            if (
                "pdf" in doc_title.lower()
                or "agenda" in doc_link.attrib["href"].lower()
            ):
                # Only use agenda scraped from page
                links = [l for l in links if "agen" not in l["title"].lower()]
                links.append({"title": "Agenda", "href": doc_link.attrib["href"]})
        return links

    def _parse_source(self, item):
        return item.css("a[itemprop='url']::attr(href)").extract_first()
