import pytest
import json

from documenters_aggregator.spiders.cook_board import Cook_boardSpider


test_response = []
with open('tests/files/cook_board.txt') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = Cook_boardSpider()
parsed_items = [item for item in spider._parse_events(test_response)]


def test_name():
    assert parsed_items[25]['name'] == 'Board of Commissioners'


def test_description():
    expected_description = ('https://cook-county.legistar.com/'
                            'View.ashx?M=A&ID=521583&GUID=EA23CB0D'
                            '-2E10-47EA-B4E2-EC7BA3CB8D76')
    assert parsed_items[25]['description'] == expected_description


def test_start_time():
    assert parsed_items[25]['start_time'].isoformat() == '2017-09-13T11:00:00-05:00'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None


def test_id():
    assert parsed_items[25]['id'] == 'cook_board/201709131100/x/board_of_commissioners'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


def test_status():
    assert parsed_items[25]['status'] == 'passed'


def test_location():
    assert parsed_items[25]['location'] == {
        'url': None,
        'name': None,
        'address': 'Cook County Building, Board Room, 118 North Clark Street, Chicago, Illinois',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_sources():
    assert parsed_items[25]['sources'] == [{
        'url': 'https://cook-county.legistar.com/DepartmentDetail.aspx?ID=20924&GUID=B78A790A-5913-4FBF-8FBF-ECEE445B7796',
        'note': ''}]


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
