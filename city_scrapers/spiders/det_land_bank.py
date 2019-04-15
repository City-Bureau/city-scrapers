import json
import re

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse


class DetLandBankSpider(CityScrapersSpider):
    name = 'det_land_bank'
    agency = 'Detroit Land Bank Authority'
    timezone = 'America/Detroit'
    allowed_domains = ['buildingdetroit.org']
    start_urls = ['https://buildingdetroit.org/events/meetings']

    def parse(self, response):
        data = response.xpath(
            'substring-before(substring-after(//script[contains(text(), "var meeting =")]/text()'
            ', "var meeting ="), "\n")'
        ).extract_first()
        entries = json.loads(data.strip()[:-1])

        for item in entries:
            meeting = Meeting(
                title=item['title_tmp'],
                description=item['content'],
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                time_notes='',
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting['status'] = self._get_status(meeting, text=item['status'])
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        if 'board of director' in item['category_type'].lower():
            return BOARD
        return COMMITTEE

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        return dateparse(item['start'])

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address':
                re.sub(
                    r'\s+', ' ', '{} {}, {} {}'.format(
                        item['address'], item['city'], item['state'], item['zipcode']
                    )
                ).strip(),
            'name': '',
        }

    def _parse_links(self, item):
        """Parse or generate documents."""
        if item['file_path']:
            return [{'href': item['file_path'], 'title': 'Minutes'}]
        return []
