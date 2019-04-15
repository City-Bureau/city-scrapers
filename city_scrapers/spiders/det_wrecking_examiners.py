from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetWreckingExaminersSpider(CityScrapersSpider):
    name = 'det_wrecking_examiners'
    agency = 'Detroit Wrecking Contractors Board of Examiners'
    timezone = 'America/Detroit'
    allowed_domains = ['www.detroitmi.gov']
    start_urls = [
        'https://www.detroitmi.gov/government/boards/board-wrecking-contractors-examiners/board-wrecking-contractors-meetings'  # noqa
    ]
    location = {
        'name': 'Coleman A. Young Municipal Center, Room 412',
        'address': '2 Woodward Avenue, Detroit, MI 48226',
    }

    def parse(self, response):
        for item in response.xpath(
            '//div[contains(@class, "view-header")]//p[strong[contains(string(), '
            '"The Board of Wrecking Contractors")]]/following-sibling::p/text()'
        ).extract():
            meeting = Meeting(
                title='Board of Wrecking Contractors Examiners',
                description='',
                classification=BOARD,
                start=self._parse_start(item),
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

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        try:
            meeting_date = parse(item)
            return datetime.combine(meeting_date.date(), time(13))
        except ValueError:
            pass
