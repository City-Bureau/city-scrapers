import re
from datetime import datetime, time

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class DetEntertainmentCommissionSpider(CityScrapersSpider):
    name = 'det_entertainment_commission'
    agency = 'Detroit Entertainment Commission'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitsentertainmentcommission.com']
    start_urls = ['https://www.detroitsentertainmentcommission.com/services']
    location = {
        'name': 'Coleman A. Young Municipal Center',
        'address': '2 Woodward Ave, Detroit, MI 48226',
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting = Meeting(
            title='Entertainment Commission',
            description='',
            classification=COMMISSION,
            start=self._parse_start(response),
            end=None,
            time_notes='',
            all_day=False,
            location=self.location,
            links=[],
            source=response.url,
        )

        meeting['status'] = self._get_status(meeting)
        meeting['id'] = self._get_id(meeting)
        yield meeting

    def _parse_start(self, response):
        """Parse start datetime."""
        response_text = re.sub(
            r'\s+', ' ', ' '.join(response.css('[data-packed="true"] span::text').extract())
        ).strip()
        date_match = re.search(r'(?<=Next Meeting Date)[:\w\d\s,]+\d{4}', response_text).group()
        month_day = re.search(r'\w+\s+\d{1,2}', date_match).group()
        year_str = re.search(r'\d{4}', date_match).group()
        dt = datetime.strptime('{} {}'.format(month_day, year_str), '%B %d %Y')
        return datetime.combine(dt.date(), time(17))
