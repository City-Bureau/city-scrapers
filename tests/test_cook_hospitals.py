from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from tests.utils import file_response

from city_scrapers.spiders.cook_hospitals import CookHospitalsSpider

test_response = file_response(
    'files/cook_hospitals.html',
    url='http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/'
)
spider = CookHospitalsSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'Meetings of the Board of Directors'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2017, 1, 27, 9)


def test_end():
    assert parsed_items[0]['end'] is None


def test_time_notes():
    assert parsed_items[0]['time_notes'] == ''


def test_links():
    assert parsed_items[0]['links'] == [
        {
            'href':
                'http://www.cookcountyhhs.org/wp-content/uploads/2016/01/01-27-17-Board-Agenda.pdf',
            'title': 'Agenda and materials'
        },
        {
            'href':
                'http://www.cookcountyhhs.org/wp-content/uploads/2017/02/01-27-17-Board-scan-Minutes.pdf',  # noqa
            'title': 'Minutes'
        },
    ]
    assert parsed_items[-1]['links'] == []


def test_id():
    assert parsed_items[0]['id'
                           ] == 'cook_hospitals/201701270900/x/meetings_of_the_board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': '1900 W. Polk, Second Floor Conference Room, Chicago, Illinois',
    }


def test_classification():
    assert parsed_items[0]['classification'] == BOARD
    assert parsed_items[-1]['classification'] == COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item['source'
                ] == 'http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/'
