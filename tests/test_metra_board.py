import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.metra_board import Metra_boardSpider


test_response = file_response('files/metra_board.html')
spider = Metra_boardSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Metra February 2018 Board Meeting'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2018-02-21T10:30:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'metra_board/201802211030/x/metra_february_2018_board_meeting'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': '',
        'address': '547 West Jackson Boulevard, Chicago, IL',
        'coordinates': {
            'latitude': '',
            'longitude': '',
        },
    }


def test_sources():
    assert parsed_items[0]['sources'][0] == {
        'url': 'http://www.example.com',
        'note': ''
    }


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'transit'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
