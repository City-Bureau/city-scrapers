import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED

from city_scrapers.spiders.det_water_sewage_department import DetWaterSewageDepartmentSpider

with open(join(dirname(__file__), "files", "det_water_sewage_department.json"), "r") as f:
    test_response = json.load(f)

spider = DetWaterSewageDepartmentSpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]


def test_item_count():
    assert len(parsed_items) == 48


def test_title():
    assert parsed_items[3]['title'] == 'Board of Water Commissioners'


def test_description():
    assert parsed_items[3]['description'] == ''


def test_start():
    assert parsed_items[3]['start'] == datetime(2018, 7, 18, 14)


def test_end():
    assert parsed_items[3]['end'] is None


def test_id():
    assert parsed_items[3][
        'id'
    ] == 'det_water_sewage_department/201807181400/x/board_of_water_commissioners'


def test_status():
    assert parsed_items[3]['status'] == PASSED


def test_location():
    assert parsed_items[3]['location'] == {
        'name': 'Water Board Building',
        'address': '5th Floor Board Room 735 Randolph St Detroit, MI 48226'
    }


def test_source():
    assert parsed_items[3][
        'source'
    ] == 'https://dwsd.legistar.com/MeetingDetail.aspx?ID=612621&GUID=3F812456-D392-4F0F-B111-136AA94A96A3&Options=info&Search='  # noqa


def test_links():
    assert parsed_items[3]['links'] == [
        {
            'href':
                'https://dwsd.legistar.com/View.ashx?M=A&ID=612621&GUID=3F812456-D392-4F0F-B111-136AA94A96A3',  # noqa
            'title': 'Agenda'
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD
