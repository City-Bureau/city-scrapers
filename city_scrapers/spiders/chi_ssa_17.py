import re
from datetime import datetime

from city_scrapers_core.constants import CANCELLED, COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa17Spider(CityScrapersSpider):
    name = 'chi_ssa_17'
    agency = 'Chicago Special Service Area #17 Lakeview East'
    timezone = 'America/Chicago'
    start_urls = ['https://lakevieweast.com/ssa-17/']
    location = {
        'name': 'Lakeview East Chamber of Commerce',
        'address': '3208 N Sheffield Ave Chicago, IL 60657',
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meetings_header = [
            h for h in response.css('.post-content h3') if 'Meeting Dates' in h.extract()
        ][0]
        minutes = self._parse_minutes(response)
        meeting_list = meetings_header.xpath('following-sibling::ul')[0].css('li')

        for item in meeting_list:
            start = self._parse_start(item)
            meeting = Meeting(
                title='SSA #17 Commission',
                description='',
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes='Estimated 2 hour duration',
                all_day=False,
                location=self.location,
                links=minutes.get(start.date(), []),
                source=response.url,
            )
            meeting['status'] = self._get_status(meeting)
            if len(item.css('ul')):
                meeting['status'] = CANCELLED
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_start(self, item):
        """Parse start datetime"""
        date_str = re.sub(r'[\.\*]', '', item.xpath('./text()').extract_first()).strip()
        date_str = re.sub(r'\s(?=[apm]{2}$)', '', date_str)
        return datetime.strptime(
            ', '.join(date_str.split(', ')[-2:]).strip(),
            '%B %d, %Y at %I:%M%p',
        )

    def _parse_minutes(self, response):
        """Parse minutes from separate list"""
        minutes_header = [
            h for h in response.css('.post-content h3') if 'Meeting Minutes' in h.extract()
        ][0]

        minutes_dict = {}
        minutes_list = minutes_header.xpath('following-sibling::ul')[0].css('a')

        for minutes in minutes_list:
            minutes_text = minutes.xpath('./text()').extract_first()
            minutes_date = datetime.strptime(
                ', '.join(minutes_text.split(', ')[-2:]),
                '%B %d, %Y',
            ).date()
            minutes_dict[minutes_date] = [{'href': minutes.attrib['href'], 'title': 'Minutes'}]

        return minutes_dict
