import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from freezegun import freeze_time

from city_scrapers.spiders.det_great_lakes_water_authority import DetGreatLakesWaterAuthoritySpider

with open(join(dirname(__file__), "files", "det_great_lakes_water_authority.json"), "r") as f:
    test_response = json.load(f)

freezer = freeze_time('2018-12-27')
freezer.start()

spider = DetGreatLakesWaterAuthoritySpider()
parsed_items = [item for item in spider.parse_legistar([(item, None) for item in test_response])]

freezer.stop()


def test_title():
    assert parsed_items[0]['title'] == 'Audit Committee'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2019, 12, 20, 8)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'det_great_lakes_water_authority/201912200800/x/audit_committee'


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Water Board Building',
        'address': '735 Randolph St Detroit, MI 48226'
    }


def test_source():
    assert parsed_items[0]['source'] == 'https://glwater.legistar.com/Calendar.aspx'


def test_classification():
    assert parsed_items[0]['classification'] == COMMITTEE


def test_links():
    assert parsed_items[0]['links'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
