from datetime import date, time
from unittest.mock import MagicMock

import pytest
from tests.utils import file_response

from city_scrapers.constants import BOARD, PASSED
from city_scrapers.spiders.chi_library import ChiLibrarySpider

session = MagicMock()
res_mock = MagicMock()
res_mock.status_code = 200
res_mock.text = file_response('files/chi_library.json').text
session.get.return_value = res_mock
test_response = file_response(
    'files/chi_library.html',
    url=('https://www.chipublib.org/'
         'board-of-directors/board-meeting-schedule/'),
)
spider = ChiLibrarySpider(session=session)
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors'


def test_description():
    assert parsed_items[0]['description'] == (
        'There are no meetings in February, July and August. '
        'Entry into these meetings is permitted at 8:45 a.m.'
    )


def test_start():
    assert parsed_items[0]['start']['date'] == date(2017, 1, 17)
    assert parsed_items[0]['start']['time'] == time(9, 0)


def test_id():
    assert parsed_items[0]['id'] == ('chi_library/201701170900/x/board_of_directors')


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_location():
    assert parsed_items[0]['location'] == {
        'address': '400 S. State Street, CHICAGO IL 60605',
        'coordinates': {
            'latitude': None,
            'longitude': None
        },
        'name': ('Harold Washington Library Center, '
                 'Multi-Purpose Room, Lower Level'),
        'url': None
    }


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'note': 'Agenda',
            'url':
                'https://www.chipublib.org/news/board-of-directors-meeting-agenda-january-17-2017/'
        },
        {
            'note': 'Minutes',
            'url':
                'https://www.chipublib.org/news/board-of-directors-meeting-minutes-january-17-2017/'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_name_param(item):
    assert item['name'] == 'Board of Directors'


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end']['date'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day_param(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': ('https://www.chipublib.org/board-of-directors'
                '/board-meeting-schedule/'),
        'note': ''
    }]
