import pytest

from tests.utils import file_response
from datetime import date
from datetime import time

from city_scrapers.constants import BOARD
from city_scrapers.spiders.il_metra_board import IlMetraBoardSpider


test_response = file_response('files/il_metra_board.html')
spider = IlMetraBoardSpider()
parsed_items = [
    item for item in spider.parse(test_response) if isinstance(item, dict)
]


def test_name():
    assert parsed_items[0]['name'] == 'Metra February 2018 Board Meeting'


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


def test_start():
    EXPECTED_START = {
        'date': date(2018, 2, 21),
        'time': time(10, 30),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': 'West Loop',
        'name': '',
        'address': '547 West Jackson Boulevard, Chicago, IL',
    }


def test_sources():
    assert parsed_items[0]['sources'][0] == {
        'url': 'http://www.example.com',
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == (
        'il_metra_board/201802211030/x/metra_february_2018_board_meeting'
    )


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_documents():
    assert parsed_items[0]['documents'] == []
    assert parsed_items[12]['documents'] == [
        {
            'url': (
                'http://metrarr.granicus.com/AgendaViewer.php'
                '?view_id=5&clip_id=276'
            ),
            'note': 'Agenda',
        },
        {
            'url': (
                'http://metrarr.granicus.com/MinutesViewer.php'
                '?view_id=5&clip_id=276&doc_id='
                '67620acc-fc9b-11e7-8dcb-00505691de41'
            ),
            'note': 'Minutes',
        },
        {
            'url': (
                'http://metrarr.granicus.com/MediaPlayer.php'
                '?view_id=5&clip_id=276'
            ),
            'note': 'Video',
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert parsed_items[0]['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end']['date'] == item['start']['date']
    assert item['end']['time'] is None
