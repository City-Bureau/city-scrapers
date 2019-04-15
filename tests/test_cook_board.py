import json
from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD, PASSED

from city_scrapers.spiders.cook_board import CookBoardSpider

test_response = []
with open('tests/files/cook_board.txt') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = CookBoardSpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]


def test_count():
    assert len(parsed_items) == 167


def test_title():
    assert parsed_items[25]['title'] == 'Board of Commissioners'


def test_description():
    assert parsed_items[25]['description'] == ''


def test_start():
    assert parsed_items[25]['start'] == datetime(2017, 9, 13, 11)


def test_end():
    assert parsed_items[25]['end'] is None


def test_id():
    assert parsed_items[25]['id'] == 'cook_board/201709131100/x/board_of_commissioners'


def test_classification():
    assert parsed_items[25]['classification'] == BOARD


def test_status():
    assert parsed_items[25]['status'] == PASSED


def test_location():
    assert parsed_items[25]['location'] == {
        'name': '',
        'address': 'Cook County Building, Board Room, 118 North Clark Street, Chicago, Illinois',
    }


def test_source():
    assert parsed_items[25][
        'source'
    ] == 'https://cook-county.legistar.com/DepartmentDetail.aspx?ID=20924&GUID=B78A790A-5913-4FBF-8FBF-ECEE445B7796'  # noqa


def test_links():
    assert parsed_items[25]['links'] == [
        {
            'href':
                'https://cook-county.legistar.com/View.ashx?M=A&ID=521583&GUID=EA23CB0D-2E10-47EA-B4E2-EC7BA3CB8D76',  # noqa
            'title': 'Agenda'
        },
        {
            'title': 'Video',
            'href': 'https://cook-county.legistar.comVideo.aspx?Mode=Granicus&ID1=1858&Mode2=Video'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
