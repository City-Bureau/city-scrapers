from datetime import datetime

import pytest  # noqa
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import BOARD, TENTATIVE
from city_scrapers.spiders.det_police_department import DetPoliceDepartmentSpider

freezer = freeze_time('2019-02-22')
freezer.start()

test_response = file_response(
    'files/det_police_department.html',
    url='https://detroitmi.gov/events/board-police-commissioners-2-28-19'
)
spider = DetPoliceDepartmentSpider()
item = spider.parse_event_page(test_response)

freezer.stop()


def test_title():
    assert item['title'] == 'Board of Police Commissioners'


def test_description():
    assert item['description'] == ''


def test_start():
    assert item['start'] == datetime(2019, 2, 28, 15, 0)


def test_end():
    assert item['end'] == datetime(2019, 2, 28, 18, 0)


def test_time_notes():
    assert item['time_notes'] == 'Estimated 3 hour duration'


def test_id():
    assert item['id'] == 'det_police_department/201902281500/x/board_of_police_commissioners'


def test_status():
    assert item['status'] == TENTATIVE


def test_location():
    assert item['location'] == {
        'name': 'Detroit Public Safety Headquarters',
        'address': '1301 3rd Street Detroit, MI 48226'
    }


def test_source():
    assert item['source'] == 'https://detroitmi.gov/events/board-police-commissioners-2-28-19'


def test_links():
    assert item['links'] == []


def test_all_day():
    assert item['all_day'] is False


def test_classification():
    assert item['classification'] == BOARD
