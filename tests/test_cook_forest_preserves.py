import json
from datetime import date, time

import pytest
from freezegun import freeze_time

from city_scrapers.constants import BOARD, COMMITTEE, PASSED, TENTATIVE
from city_scrapers.spiders.cook_forest_preserves import CookForestPreservesSpider

freezer = freeze_time('2018-12-19')
freezer.start()
with open('tests/files/cook_forest_preserve.json', 'r') as f:
    test_response = json.load(f)
spider = CookForestPreservesSpider()
parsed_items = [item for item in spider._parse_events(test_response)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'FPD Board of Commissioners'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2019, 12, 17),
        'time': time(10, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2019, 12, 17),
        'time': time(13, 00),
        'note': 'Estimated 3 hours after start time'
    }


def test_id():
    assert parsed_items[0]['id'
                           ] == 'cook_forest_preserves/201912171000/x/fpd_board_of_commissioners'


def test_classification():
    assert parsed_items[0]['classification'] == BOARD
    assert parsed_items[30]['classification'] == COMMITTEE


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE
    assert parsed_items[20]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': 'Cook County Building, Board Room 118 North Clark Street, Chicago, Illinois',
        'neighborhood': ''
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url':
            'https://fpdcc.legistar.com/DepartmentDetail.aspx?ID=24752&GUID=714693C0-DBCE-4D3B-A3D9-A5FCBE27378B',  # noqa
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []
    assert parsed_items[20]['documents'] == [
        {
            'url':
                'https://fpdcc.legistar.com/View.ashx?M=A&ID=584806&GUID=C00EFBA7-F086-41D9-B0EE-A9057114D3EE',  # noqa
            'note': 'Agenda'
        },
        {
            'note': 'Video',
            'url': 'https://fpdcc.legistar.com/Video.aspx?Mode=Granicus&ID1=437&Mode2=Video'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
