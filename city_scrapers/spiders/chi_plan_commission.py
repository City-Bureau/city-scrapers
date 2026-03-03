import re
from datetime import datetime

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Selector


class ChiPlanCommissionSpider(CityScrapersSpider):
    name = "chi_plan_commission"
    agency = "Chicago Plan Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/dcd/chicago-plan-commission/meetings--agendas---video-archives.html?wcmmode=disabled"
    ]
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        },
    }
    location = {"name": "City Hall", "address": "121 N LaSalle St Chicago, IL 60602"}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        last_year = datetime.today().replace(year=datetime.today().year - 1)

        table_groups = []

        current_year_heading = response.xpath(
            "//h3[contains(., 'Meeting Schedule')][1]"
        )
        current_year_text = " ".join(current_year_heading.xpath(".//text()").getall()).strip()
        current_year_match = re.search(r"\b(\d{4})\b", current_year_text)

        if current_year_match:
            current_year = current_year_match.group(1)
            current_year_table = current_year_heading.xpath("following::table[1]")
            if current_year_table:
                table_groups.append((current_year, current_year_table))

        for card in response.css(".accordion-item.card"):
            year_str = card.css(".cds-accordion-title::text").get()
            if not year_str or not re.search(r"\d{4}", year_str):
                continue

            for tbl in card.css(".card-body table"):
                table_groups.append((year_str.strip(), tbl))

        for year_str, meeting_group in table_groups:
            year_str = re.search(r"\d{4}", year_str).group()

            for column in meeting_group.css("td").extract():
                for item_str in re.split(r"\<br\s*\/?\>", column):
                    item = Selector(text=item_str)

                    item_text = " ".join(item.css("*::text").extract()).strip()
                    if not item_text:
                        continue

                    if "postpon" in item_text.lower():
                        continue

                    start = self._parse_start(item, year_str)
                    if start is None or (
                        start < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                    ):
                        continue

                    links = self._parse_links(item, response)

                    detail_links = [
                        link["href"]
                        for link in links
                        if link["href"].endswith(".html")
                        and "postpone" not in link["title"].lower()
                    ]

                    if detail_links:
                        detail_url = detail_links[0]

                        yield response.follow(
                            detail_url,
                            callback=self._parse_detail,
                            cb_kwargs={"start": start, "list_links": links},
                            headers=self.custom_settings["DEFAULT_REQUEST_HEADERS"],
                        )
                        continue

                    meeting = Meeting(
                        title="Commission",
                        description="",
                        classification=COMMISSION,
                        start=start,
                        end=None,
                        time_notes="",
                        all_day=False,
                        location=self.location,
                        source=response.url,
                        links=links,
                    )
                    meeting["id"] = self._get_id(meeting)
                    meeting["status"] = self._get_status(meeting)
                    yield meeting

    def _parse_detail(self, response, **kwargs):
        start = self._parse_detail_start(response, kwargs["start"])
        list_links = kwargs.get("list_links", [])

        detail_links = self._parse_detail_links(response)

        merged = []
        seen = set()
        
        # Filter out agenda links from main page/html
        filtered_list_links = [
            link for link in list_links 
            if "agenda" not in link["title"].lower()
        ]
        
        for lnk in (filtered_list_links + detail_links):
            href = lnk.get("href")
            if not href or href in seen:
                continue
            seen.add(href)
            merged.append(lnk)

        detail_text = " ".join(response.css(".col-12 > p *::text").extract())
        location = self.location
        if "virtual" in detail_text.lower():
            location = {"name": "Virtual, see meeting details", "address": ""}

        meeting = Meeting(
            title="Commission",
            description="",
            classification=COMMISSION,
            start=start,
            end=None,
            time_notes="",
            all_day=False,
            location=location,
            source=response.url,
            links=merged,
        )
        meeting["id"] = self._get_id(meeting)
        meeting["status"] = self._get_status(meeting)
        yield meeting

    @staticmethod
    def _parse_start(item, year):
        item_text = " ".join(item.css("*::text").extract())
        date_match = re.search(r"[A-Z][a-z]{2,8}\.?\s+\d{1,2}", item_text)
        if not date_match:
            return
        return dateutil.parser.parse(" ".join([date_match.group(), year, "10:00am"]))

    def _parse_links(self, item, response):
        links = []
        for link in item.css("a"):
            links.append(
                {
                    "title": re.sub(r"\s+", " ", " ".join(link.css("*::text").extract())).strip(),
                    "href": response.urljoin(link.attrib["href"]),
                }
            )
        return links

    def _parse_detail_start(self, response, start):
        detail_text = " ".join(response.css(".col-12 > p *::text").extract())
        time_strs = re.findall(
            r"(\d{1,2}(\:\d{2})?\s+[apm\.]{2,4})", detail_text, flags=re.I
        )
        time_objs = []
        for time_str in time_strs:
            time_str = re.sub(r"[\s\.]", "", time_str[0])
            time_fmt = "%I%p"
            if ":" in time_str:
                time_fmt = "%I:%M%p"
            time_objs.append(datetime.strptime(time_str, time_fmt).time())
        if len(time_objs) > 0:
            return datetime.combine(start.date(), time_objs[0])
        return start

    def _parse_detail_links(self, response):
        links = []
        seen = set()

        link_selectors = response.css('p[style*="text-align: center"] a') + response.css('td[style*="text-align: center"] a')

        for link in link_selectors:
            href = link.attrib.get("href")
            if not href:
                continue

            href = response.urljoin(href)
            title_str = re.sub(r"\s+", " ", " ".join(link.css("*::text").getall())).strip()

            if (
                not title_str
                or "mailto:" in href
                or href.endswith("/chicago_plan_commission.html")
            ):
                continue

            if href in seen:
                continue
            seen.add(href)

            links.append({"title": title_str, "href": href})

        return links
