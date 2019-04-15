import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class DetWaterSewageDepartmentSpider(LegistarSpider):
    name = 'det_water_sewage_department'
    agency = 'Detroit Water and Sewage Department'
    timezone = 'America/Detroit'
    start_urls = ['https://dwsd.legistar.com/Calendar.aspx']
    allowed_domains = ['dwsd.legistar.com']

    def parse_legistar(self, events):
        for event, _ in events:
            meeting = Meeting(
                title=event['Name'],
                description='',
                classification=BOARD,
                start=self._parse_start(event),
                end=None,
                time_notes='',
                all_day=False,
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self._parse_source(event),
            )
            meeting['status'] = self._get_status(meeting, event['Meeting Location'])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_start(self, event):
        start_date = event.get("Meeting Date")
        start_time = event.get("Meeting Time")
        if start_date and start_time:
            if 'cancel' in start_time.lower():
                return datetime.strptime(start_date, '%m/%d/%Y')
            else:
                return datetime.strptime(
                    '{} {}'.format(start_date, start_time), '%m/%d/%Y %I:%M %p'
                )

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

    def _parse_source(self, item):
        """Parse source from meeting details if available"""
        default_source = "{}/Calendar.aspx".format(self.base_url)
        if isinstance(item.get("Meeting Details"), dict):
            return item["Meeting Details"].get("url", default_source)
        return default_source
