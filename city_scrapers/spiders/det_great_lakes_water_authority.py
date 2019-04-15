import re

from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class DetGreatLakesWaterAuthoritySpider(LegistarSpider):
    name = 'det_great_lakes_water_authority'
    agency = 'Detroit Great Lakes Water Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['glwater.legistar.com']
    start_urls = ['https://glwater.legistar.com/Calendar.aspx']

    def parse_legistar(self, events):
        for event, _ in events:
            start = self.legistar_start(event)
            meeting = Meeting(
                title=event['Name'],
                description='',
                classification=self._parse_classification(event['Name']),
                start=start,
                end=None,
                time_notes='',
                all_day=False,
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )

            meeting['status'] = self._get_status(meeting, text=event['Meeting Time'])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_classification(self, name):
        if 'board' in name.lower():
            return BOARD
        elif 'committee' in name.lower():
            return COMMITTEE
        return NOT_CLASSIFIED

    def _parse_location(self, item):
        """
        Parse location
        """
        address = item.get('Meeting Location', '')
        if address:
            address = re.sub(
                r'\s+',
                ' ',
                re.sub(r'(\n)|(--em--)|(--em)|(em--)', ' ', address),
            ).strip()
        if 'water board building' in address.lower():
            return {
                'name': 'Water Board Building',
                'address': '735 Randolph St Detroit, MI 48226',
            }
        return {
            'name': '',
            'address': address,
        }
