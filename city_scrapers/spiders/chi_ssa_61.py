import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa61Spider(CityScrapersSpider):
    name = "chi_ssa_61"
    agency = "Chicago Special Service Area #60 Hyde Park"
    timezone = "America/Chicago"
    allowed_domains = ["www.downtownhydeparkchicago.com"]
    start_urls = ["http://www.downtownhydeparkchicago.com/about/"]
    location = {
        "name": "Polsky Center for Innovation",
        "address": "1452 East 53rd Street, 2nd Floor, Chicago, IL 60615"
    }

    def parse(self, response):
        """Parse meetings on upcoming and minutes pages"""
        today = datetime.now().replace(hour=0, minute=0)
        for item in response.xpath('//div[@rel="1"]/ul/li/strong'):
            text = item.xpath('./text()').extract_first()
            if not re.search(r"[ pam\.]{2,5}", text):
                continue
            start = self._parse_start(text)
            if not start or (start < today):
                continue
            meeting = Meeting(
                title=self.agency,
                description='',
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes='',
                all_day=False,
                location=self.location,
                source=response.url,
            )
            yield meeting

    def _parse_start(self, text):
        """
        Parse start date and time.
        """
        date_match = re.search(r'[a-zA-Z]{3,9} \d{1,2}([a-z,]{1,3})? \d{4}', text)
        time_match = re.search(r'\d{1,2}:\d{2}[ pam\.]{2,5}', text)
        if date_match:
            try:
                date_str = re.sub(
                    r'(?<=\d)[a-z]{2}',
                    '',
                    date_match.group().replace(',', ''),
                )
                dt = datetime.strptime(date_str, '%B %d %Y').date()
            except ValueError:
                dt = None
        if time_match:
            time_str = time_match.group().replace('.', '').replace(' ', '')
            tm = datetime.strptime(time_str, '%I:%M%p').time()
        else:
            tm = time(10)
        if dt:
            return datetime.combine(dt, tm)
