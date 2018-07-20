import json
from datetime import date, time
import pytest

from city_scrapers.spiders.det_water_sewage_department import DetWaterSewageDepartmentSpider

test_response = []
with open('tests/files/det_water_sewage_department.json', encoding='utf-8') as f:
    test_response.extend(json.loads(f.read()))
spider = DetWaterSewageDepartmentSpider()
parsed_items = [item for item in spider._parse_events(test_response)]


def test_item_count():
    assert len(parsed_items) == 48


def test_name():
    assert parsed_items[3]['name'] == 'Board of Water Commissioners'


def test_description():
    assert parsed_items[3]['event_description'] == ''


def test_start():
    assert parsed_items[3]['start'] == {
        'date': date(2018, 7, 18), 'time': time(14, 00), 'note': ''
    }


def test_end():
    assert parsed_items[3]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[3]['id'] == 'det_water_sewage_department/201807181400/x/board_of_water_commissioners'


def test_status():
    assert parsed_items[3]['status'] == 'passed'


def test_location():
    assert parsed_items[3]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': '5th Floor Board Room, Water Board Building\n--em--Regular Meeting--em--'
    }


def test_sources():
    assert parsed_items[3]['sources'] == [{
        'url': 'https://mwrd.legistar.com/Calendar.aspx',
        'note': ''
    }]


def test_documents():
    assert parsed_items[3]['documents'] == [
        {
            'url': 'https://dwsd.legistar.com/MeetingDetail.aspx?ID=612621&GUID=3F812456-D392-4F0F-B111-136AA94A96A3&Options=info&Search=',
            'note': 'Meeting Details'
        },
        {
            'url': 'https://dwsd.legistar.com/View.ashx?M=A&ID=612621&GUID=3F812456-D392-4F0F-B111-136AA94A96A3',
            'note': 'Agenda'
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
