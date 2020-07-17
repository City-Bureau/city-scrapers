import re
from datetime import datetime

import requests
import scrapy
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNorthwestHomeEquitySpider(CityScrapersSpider):
    name = "chi_northwest_home_equity"
    agency = "Chicago Northwest Home Equity Assurance Program"
    timezone = "America/Chicago"
    start_urls = ["https://nwheap.com/category/meet-minutes-and-agendas/"]

    def parse(self, response):
        self.location_dict = {
            "3022 N. Harlem": "3022 N. Harlem Ave #2S, Chicago, IL 60634",
            "3022 N. Harlem Ave. #2S": "3022 N. Harlem Ave #2S, Chicago, IL 60634",
            "3022 Harlem Ave. #2S": "3022 Harlem Ave #2S, Chicago, IL 60634",
            "3234 N. Central Ave.": "3234 N. Central Ave, Chicago, IL 60634",
            "5363 W. Lawrence Ave.": "5363 W. Lawrence Ave, Chicago, IL 60630",
        }
        self.location_name_dict = {
            "3022 N. Harlem": "Northwest Home Equity Main Office",
            "3022 N. Harlem Ave #2S": "Northwest Home Equity Main Office",
            "3022 Harlem Ave #2S": "Northwest Home Equity Main Office",
            "3234 N. Central Ave.": "Northwest Home Equity Assurance Program",
            "5363 W. Lawrence Ave": "Jefferson Park Library",
        }
        # Before we begin, need to collect meeting minutes data -- which is
        #  contained on multiple iterative pages (/page/2 /page/3 etc)
        r = requests.get("https://nwheap.com/category/meet-minutes-and-agendas/")
        article_response = scrapy.http.HtmlResponse(r.url, body=r.content).xpath(
            "//article"
        )
        pageNum = 1
        article_all_pages = []
        while (r.status_code) == 200:
            for article in article_response:
                article_all_pages.append(article)
            pageNum += 1
            r = requests.get(
                "https://nwheap.com/category/meet-minutes-and-agendas/page/"
                + str(pageNum)
                + "/"
            )
            article_response = scrapy.http.HtmlResponse(r.url, body=r.content).xpath(
                "//article"
            )
        # Now moving onto the main parse of the meetings list
        meeting_response = []
        future_meetings = response.xpath("/html/body/div[1]/div[2]/aside[1]/ul/li")
        for meet in future_meetings:
            if meet.re(r"\d\d/\d\d/\d\d\d\d"):
                meeting_response.append(meet)
        past_meetings = response.xpath("/html/body/div[1]/div[2]/aside[2]/ul/li")
        for meet in past_meetings:
            if meet.re(r"\d\d/\d\d/\d\d\d\d"):
                meeting_response.append(meet)
        for item in meeting_response:
            has_related_article_page = False
            meeting_date = item.re_first(r"\d\d/\d\d/\d\d\d\d")
            for article in article_all_pages:
                article_date = article.xpath(".//a/text()")[0].re_first(
                    r"\S* \d\d?, ?20\d\d"
                )
                if article_date is None:
                    continue
                date_obj = datetime.strptime(article_date, "%B %d, %Y").date()
                if date_obj.strftime("%m/%d/%Y") == meeting_date:
                    has_related_article_page = True
                    article_detail = article
                    details_page_url = article.re_first(r'http[^"]*')
                    r1 = requests.get(details_page_url)
                    details_page_response = scrapy.http.HtmlResponse(
                        r1.url, body=r1.content
                    )
            if not has_related_article_page:
                details_page_response = None
                article_detail = None
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(article_detail),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(details_page_response),
                source=self._parse_source(response),
            )
            yield meeting

    def _parse_title(self, item):
        return item.xpath(".//a/text()").extract_first()

    def _parse_description(self, item):
        if item is None or item.xpath(".//p/text()").extract_first() is None:
            return "No Description"
        else:
            return item.xpath(".//p/text()").extract_first()

    def _parse_classification(self, item):
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        date_str = item.re_first(r"\d\d/\d\d/\d\d\d\d")
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
        time_Str = item.re_first(r"\d:\d\d [ap]m")
        time_Time = datetime.strptime(time_Str, "%I:%M %p").time()
        return datetime.combine(date_obj, time_Time)

    def _parse_end(self, item):
        date_str = item.re_first(r"\d\d/\d\d/\d\d\d\d")
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
        time_Str = item.re(r"\d:\d\d [ap]m")[-1]
        time_Time = datetime.strptime(time_Str, "%I:%M %p").time()
        return datetime.combine(date_obj, time_Time)

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        locationRaw = item.re_first(r"<li>\d\d*? \S* \S* \S*? ?</li>")
        if locationRaw is None:
            return {"name": "", "address": "No Address Found"}
        locationAddy = re.sub(r" ?</?li>", "", locationRaw)
        if locationAddy in self.location_dict.keys():
            return {
                "name": self.location_name_dict[locationAddy],
                "address": self.location_dict[locationAddy],
            }
        else:
            return {"name": "", "address": locationAddy}

    def _parse_links(self, details_page):
        if details_page is None:
            return [{"href": "", "title": ""}]
        link_dict_list = details_page.xpath('//div[@class="entry-content"]').xpath(
            ".//a[@href]"
        )
        links = []
        dupe_checker = []
        for link_dict in link_dict_list:
            href = link_dict.attrib["href"]
            filename = re.sub(
                "-",
                " ",
                re.sub(r".pdf|.docx?", "", link_dict.attrib["href"].split("/")[-1]),
            ).title()
            if href not in dupe_checker:
                dupe_checker.append(href)
                links.append({"href": href, "title": filename})
        return links

    def _parse_source(self, response):
        return response.url
