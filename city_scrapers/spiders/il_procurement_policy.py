import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlProcurementPolicySpider(CityScrapersSpider):
    name = "il_procurement_policy"
    agency = "Illinois Procurement Policy Board"
    timezone = "America/Chicago"
    start_urls = [
        'https://www2.illinois.gov/sites/ppb/Pages/future_board_minutes.aspx', 
        'https://www2.illinois.gov/sites/ppb/Pages/board_minutes.aspx'
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if 'future' in response.url:
            yield from self._upcoming_meetings(response)
        else:
            yield from self._prev_meetings(response)

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title_str = item['title'].split()
        if not len(title_str):
            return ""
        name_str = title_str[len(title_str) - 1] + " Board Meeting Minutes"
        return name_str

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        time_object = time(10,0)
        date_str = " ".join(item.css("*::text").extract()).strip()
        date_str = re.sub("Agenda.pdf", "", date_str).strip()
        date_object = datetime.strptime(date_str, "%B %d, %Y").date()
        return datetime.combine(date_object, time_object)

    def _parse_links(self, item, response):
        """Parse or generate links."""
        links = []
        title_str = " ".join(item.css("*::text").extract()).strip()
        if 'pdf' in title_str:
            title_str = re.sub("Agenda.pdf", "", title_str).strip()
            title_str += " Agenda"
        links.append({
            'title': title_str,
            'href': response.urljoin(item.attrib['href']),
        })
        return links

    def _parse_past_links(self, response):
        """parse start datetime as a naive datetime object"""
        links = []
        for item in response.css(".ms-rtestate-field p a"):
            title_str = " ".join(item.css("*::text").extract()).strip()
            title_str = re.sub(".pdf", "", title_str).strip()
            title_str = title_str.replace("\u200b", "")
            links.append({
                'title': title_str,
                'href': response.urljoin(item.attrib['href'])
            })
        for item in response.css(".ms-rtestate-field .list-unstyled li a"):
            title_str = " ".join(item.css("*::text").extract()).strip()
            title_str = re.sub(".pdf", "", title_str).strip()
            if '- Amended' in title_str:
                title_str = title_str.replace("- Amended", "").strip()
            links.append({
                'title': title_str,
                'href': response.urljoin(item.attrib['href'])
            })
        return links

    def _past_start(self, item):
        """parse or generate links from past meetings"""
        time_object = time(10,0)
        date_str = item['title']
        if not len(date_str):
            return datetime.now()
        if '.pdf' in date_str:
            date_str = re.sub(".pdf", "", date_str).strip()
        date_str = date_str.replace('\u200b', '').strip()
        date_object = datetime.strptime(date_str, "%B %d, %Y").date()
        return datetime.combine(date_object, time_object)

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
    
    def _upcoming_meetings(self, response):
        for item in response.css(".ms-rtestate-field p strong a"):
            meeting = Meeting(
                title='Procurement Policy Board',
                description='',
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes='End time not specified',
                location = {
                    'name': 'Stratton Office Building',
                    'address': '401 S Spring St, Springfield, IL 62704',
                },
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _prev_meetings(self, response):
        meets = self._parse_past_links(response)
        for item in meets:
            meeting = Meeting(
                title= self._parse_title(item),
                description='',
                classification=BOARD,
                start=self._past_start(item),
                end=None,
                all_day=False,
                time_notes='End time not specified',
                location = {
                    'name': 'Stratton Office Building',
                    'address': '401 S Spring St, Springfield, IL 62704',
                },
                links=item,
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting