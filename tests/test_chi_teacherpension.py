import pytest

from tests.utils import file_response
from datetime import date
from datetime import time
from city_scrapers.constants import BOARD, PASSED, CONFIRMED, TENTATIVE
from city_scrapers.spiders.chi_teacherpension import ChiTeacherPensionSpider


test_response = file_response('files/chi_teacherpension.htm')
spider = ChiTeacherPensionSpider()
parsed_items = [
    item for item in spider.parse(test_response) if isinstance(item, dict)
]


def test_name():
    assert parsed_items[0]['name'] == 'Regular Board Meeting'


def test_start_time():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 5, 17), 'time': time(9, 30), 'note': ''
    }


def test_end_time():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 5, 17), 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == (
        'chi_teacherpension/201805170930/'
        'x/regular_board_meeting'
    )


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[4]['status'] == CONFIRMED
    assert parsed_items[5]['status'] == TENTATIVE


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'address': '203 North LaSalle Street, Suite 2600, Board Room',
        'name': 'CTPF office',
        'neighborhood': 'Loop',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': 'http://www.example.com', 'note': ''
    }]
