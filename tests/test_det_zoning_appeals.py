from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_zoning_appeals import DetZoningAppealsSpider

freezer = freeze_time('2019-02-22')
freezer.start()

test_response = file_response(
    join(dirname(__file__), "files", "det_zoning_appeals.html"),
    url='https://detroitmi.gov/node/16766'
)
spider = DetZoningAppealsSpider()
item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item['title'] == 'Board of Zoning Appeals - Docket'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 2, 26, 9, 0)


def test_end():
    assert item['end'] == datetime(2019, 2, 26, 14, 0)


def test_time_notes():
    assert item['time_notes'] == ''


def test_id():
    assert item['id'] == 'det_zoning_appeals/201902260900/x/board_of_zoning_appeals_docket'


def test_status():
    assert item['status'] == TENTATIVE


def test_location():
    assert item['location'] == {
        'name': 'Erma L. Henderson Auditorium',
        'address': '2 Woodward Avenue, Suite 1300 Detroit, MI 48226'
    }


def test_source():
    assert item['source'] == 'https://detroitmi.gov/node/16766'


def test_links():
    assert item['links'] == [{
        'title': 'Feb 26, 2019.pdf',
        'href':
            'https://detroitmi.gov/sites/detroitmi.localhost/files/events/2019-02/Feb%2026%2C%202019.pdf'  # noqa
    }]


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == BOARD
