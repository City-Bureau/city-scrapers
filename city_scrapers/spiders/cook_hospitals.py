import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookHospitalsSpider(CityScrapersSpider):
    name = 'cook_hospitals'
    agency = 'Cook County Health and Hospitals System'
    timezone = 'America/Chicago'
    allowed_domains = ['cookcountyhealth.org']
    start_urls = [
        'https://cookcountyhealth.org/about/board-of-directors/board-committee-meetings-agendas-minutes/'  # noqa
    ]
    custom_settings = {'ROBOTSTXT_OBEY': False}
    location = {
        'name': '',
        'address': '1950 W Polk St, Conference Room 5301, Chicago, IL 60612',
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # Only pull from first two year sections because it goes back pretty far
        for item in response.css(
            ".eael-tabs-content > .clearfix:first-child .elementor-post, "
            ".eael-tabs-content > .clearfix:nth-child(2) .elementor-post"
        ):
            title, start = self._parse_title_start(item)
            if start is None:
                continue
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
                start=start,
                end=None,
                time_notes="Confirm time in agenda",
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    @staticmethod
    def _parse_title_start(item):
        """Get meeting title and start datetime from item's text"""
        title_str = item.css('.elementor-heading-title::text').extract_first()
        date_match = re.search(r'\w{3,9} \d{1,2},? \d{4}', title_str)
        if not date_match:
            return None, None
        date_str = date_match.group().replace(',', '')

        title = re.sub(r'(\w+day,?\s+|\w{3,9} \d{1,2},? \d{4}|,)', '', title_str).strip()
        if 'special' not in title.lower():
            title = title.replace('Meeting', '').strip()

        start = datetime.strptime(date_str, '%B %d %Y')
        # Assign time based off of typical meeting times
        if any(w in title.lower() for w in ['board', 'human resources', 'audit']):
            start = start.replace(hour=9)
        elif 'quality' in title.lower():
            start = start.replace(hour=10)
        elif 'finance' in title.lower():
            start = start.replace(hour=8, minute=30)
        elif 'managed care' in title.lower():
            start = start.replace(hour=10, minute=30)
        return title, start

    @staticmethod
    def _parse_classification(title):
        if 'board' in title.lower():
            return BOARD
        return COMMITTEE

    @staticmethod
    def _parse_links(item):
        links = []
        for link in item.css('.elementor-icon-list-item a'):
            links.append({
                'href': link.attrib['href'],
                'title': ' '.join(link.css('::text').extract()).strip(),
            })
        return links

    def _parse_location(self, item):
        """Parse location"""
        loc_text = item.css(
            '.elementor-column:first-child li span.elementor-post-info__item::text'
        ).extract_first()
        if not loc_text or '5301' in (loc_text or ''):
            return self.location
        else:
            return {'name': '', 'address': loc_text.strip()}
