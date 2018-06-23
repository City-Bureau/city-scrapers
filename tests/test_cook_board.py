import pytest
import json
from datetime import date, time

from city_scrapers.spiders.cook_board import Cook_boardSpider


test_response = []
with open('tests/files/cook_board.txt') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = Cook_boardSpider()
parsed_items = [item for item in spider._parse_events(test_response)]


def test_name():
    assert parsed_items[25]['name'] == 'Board of Commissioners'


def test_description():
    assert parsed_items[25]['event_description'] == ''


def test_start():
    EXPECTED_START = {
        'date': date(2017, 9, 13),
        'time': time(11, 00),
        'note': ''
    }
    assert parsed_items[25]['start'] == EXPECTED_START


def test_end():
    EXPECTED_END = {
        'date': date(2017, 9, 13),
        'time': time(14, 00),
        'note': 'Estimated 3 hours after start time'
    }
    assert parsed_items[25]['end'] == EXPECTED_END


def test_id():
    assert parsed_items[25]['id'] == 'cook_board/201709131100/x/board_of_commissioners'


def test_classification():
    assert parsed_items[25]['classification'] == 'Board'


def test_status():
    assert parsed_items[25]['status'] == 'passed'


def test_location():
    assert parsed_items[25]['location'] == {
        'name': '',
        'address': 'Cook County Building, Board Room, 118 North Clark Street, Chicago, Illinois',
        'neighborhood': ''
    }


def test_sources():
    assert parsed_items[25]['sources'] == [
        {
            'url': 'https://cook-county.legistar.com/DepartmentDetail.aspx?ID=20924&GUID=B78A790A-5913-4FBF-8FBF-ECEE445B7796',
            'note': ''
        }
    ]


def test_documents():
    assert parsed_items[25]['documents'] == [
        {
            'note': 'Meeting Details', 
            'url': 'https://cook-county.legistar.com/MeetingDetail.aspx?ID=521583&GUID=EA23CB0D-2E10-47EA-B4E2-EC7BA3CB8D76&Options=info&Search='
        },
        {
            'url': 'https://cook-county.legistar.com/View.ashx?M=A&ID=521583&GUID=EA23CB0D-2E10-47EA-B4E2-EC7BA3CB8D76',
            'note': 'Agenda'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
