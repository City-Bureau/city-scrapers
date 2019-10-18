import re

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class DetWaterSewageDepartmentSpider(LegistarSpider):
    name = 'det_water_sewage_department'
    agency = 'Detroit Water and Sewage Department'
    timezone = 'America/Detroit'
    start_urls = ['https://dwsd.legistar.com/Calendar.aspx']

    def parse_legistar(self, events):
        for event, _ in events:
            meeting = Meeting(
                title=event['Name'],
                description='',
                classification=BOARD,
                start=self.legistar_start(event),
                end=None,
                time_notes='',
                all_day=False,
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )
            meeting['status'] = self._get_status(meeting, event['Meeting Location'])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_location(self, item):
        """
        Parse location
        """
        address = item.get('Meeting Location', None)
        if address:
            address = re.sub(
                r'\s+',
                ' ',
                re.sub(r'(\n)|(--em--)|(--em)|(em--)', ' ', address),
            ).strip()

        if 'water board' in address.lower():
            addr_split = address.split(', ')
            water_board_address = '735 Randolph St Detroit, MI 48226'
            if 'room' in addr_split[0].lower():
                address = '{} {}'.format(addr_split[0], water_board_address)
            else:
                address = water_board_address
            return {
                'name': 'Water Board Building',
                'address': address,
            }
        return {
            'name': '',
            'address': address,
        }
