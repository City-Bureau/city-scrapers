import re
from urllib.parse import urljoin, urlparse

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse


class ChiPubHealthSpider(CityScrapersSpider):
    name = "chi_pubhealth"
    agency = "Chicago Department of Public Health"
    timezone = "America/Chicago"
    start_urls = ["https://www.chicago.gov/city/en/depts/cdph/supp_info.html"]
    start_time = "9:00 am"
    end_time = "10:30 am"
    location = {
        "name": "DePaul Center",
        "address": "333 S State St, 2nd Floor, Room 200",
    }

    def parse(self, response):
        """
        Loop over each link to meeting pages for each year
        and then parse the meeting page.
        """
        for link in response.css(".list-group-item.list-group-item-action a"):
            text = link.css("::text").extract_first()
            if "board of health meetings" in text.lower():
                url = link.css("::attr(href)").extract_first()
                yield response.follow(url, callback=self._parse_year_page)

    def _parse_year_page(self, response):
        """
        Parse the year page and return the list of meetings,
        which appear to be monthly.
        """
        page_title = response.css("h1.page-heading::text").extract_first()
        year = re.search(r"\d{4}", page_title).group()
        base_url = self._get_base_url(response)
        for item in response.css(".accordion-item.card.section"):
            links = self._parse_links(item, base_url)
            # if there are no links then assume that month's meeting
            # has been cancelled
            if not links:
                continue
            start, end = self._parse_dates(item, year)
            meeting = Meeting(
                title="Board of Health meeting",
                description="",
                classification=BOARD,
                start=start,
                end=end,
                all_day=False,
                time_notes="",
                location=self.location,
                links=links,
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_dates(self, item, year):
        """Parse the date range from the text"""
        date_str = item.css("h3::text").extract_first()
        start_str = f"{date_str}, {year} {self.start_time}"
        end_str = f"{date_str}, {year} {self.end_time}"
        start = dateparse(start_str)
        end = dateparse(end_str)
        return start, end

    def _get_base_url(self, response):
        return f"{urlparse(response.url).scheme}://{urlparse(response.url).netloc}"

    def _parse_links(self, item, base_url):
        result = []
        links = item.css(".starlist.document li a")
        for link in links:
            text = link.css("::text").extract_first()
            clean_text = re.sub(r"\s+", " ", text)
            url = link.css("::attr(href)").extract_first()
            url_abs = urljoin(base_url, url)
            result.append({"title": clean_text, "href": url_abs})
        return result
