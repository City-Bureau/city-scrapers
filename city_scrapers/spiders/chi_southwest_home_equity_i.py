from datetime import datetime, timedelta
from io import BytesIO
import re
import requests
import sys 

import scrapy
from PyPDF2 import PdfFileReader

from city_scrapers_core.constants import PASSED, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


MONTH_REGEX = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"


def print_node(node):
    print(node.xpath('string(.)').get())



class ChiSouthwestHomeEquityISpider(CityScrapersSpider):
    name = "chi_southwest_home_equity_i"
    agency = "Chicago Southwest Home Equity Commission I"
    timezone = "America/Chicago"
    allowed_domains = ["swhomeequity.com"]
    start_urls = ["https://swhomeequity.com/agenda-%26-minutes"]
    location = {
        "name": "Southwest Home Equity Assurance office",
        "address": "5334 W. 65th Street in Chicago, Illinois"
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        # Need to filter
        table = response.xpath('body/div/div/div/div[2]/div[3]/div/div/section/div/div[2]')

        for agenda_node in table.xpath('div[@data-ux="GridCell"][contains(., \'Agenda\')]'):
            minutes_node = agenda_node.xpath('following-sibling::div[@data-ux="GridCell"][contains(., \'Minutes\')]')
            
            if self._get_link(minutes_node):
                minutes_contents = self.parse_pdf(self._get_link(minutes_node))   
                          
            if self._get_link(agenda_node):
                agenda_contents = self.parse_pdf(self._get_link(agenda_node))

            meeting = Meeting(
                title=self._parse_title(minutes_contents),
                description='',
                classification=COMMISSION,
                start=self._parse_start(agenda_node),
                end=None,
                all_day=False,
                time_notes=self._parse_time_notes(minutes_contents),
                location=self.location,
                links=self._parse_links([agenda_node, minutes_node]),
                source=self._parse_source(response),
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, text):
        name = re.search(r"Southwest Home Equity Assurance Program",text, flags=re.I)
        minutes = re.search(r"MINUTES", text, flags=re.I)
        if name and minutes:
            title = text[name.end():minutes.start()] 
            return title.replace('\n','').title()
        else:
            return 'Board Meeting'

    def parse_pdf(self, url):
        response = requests.get(url)
        pdf_obj = PdfFileReader(BytesIO(response.content))
        pdf_text = pdf_obj.getPage(0).extractText().strip()
        return pdf_text

    def _parse_start(self, node):
        date_str = self.find_date(node)
        date_object = datetime.strptime(date_str, "%B %d %Y")
        return date_object + timedelta(hours=18, minutes=30)

    def _parse_time_notes(self, item):
        return ""

    def _parse_links(self, nodes):
        links = []
        for node in nodes:
            if node:
                links.append({
                        "title": self._get_name(node),
                        "href": self._get_link(node)
                    })
        return links

    def _get_name(self, node):
        name = node.xpath('string(.)').get()
        return name

    def _get_link(self, node):
        url = node.xpath('a/@href').get()
        if url:
            return 'https:' + url
        else:
            return None
    
    def _parse_source(self, response):
        return response.url


    def find_date(self, node):
        text = self._get_name(node)
        text_block = text.replace("\n","")
        return self._use_date_regex(text_block)

    def _use_date_regex(self, text):
        month_ind = re.search(MONTH_REGEX, text, flags=re.I)
        year_ind = re.search(r"\d{4}", text[month_ind.start():]) # We need the year to come after the 
        date_str = text[month_ind.start():(month_ind.start()+year_ind.end())].replace(",","")
        return date_str

    def _parse_time_notes(self, text):
        c_t_o = re.search(r"CALL TO ORDER", text)
        commissioners = re.search(r"COMMISSIONER(S)? IN ATTENDANCE", text)
        return text[c_t_o.end(): commissioners.start()].replace('\n','')



