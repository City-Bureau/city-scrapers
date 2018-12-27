import json
from datetime import date, time

import pytest

from city_scrapers.constants import TENTATIVE
from city_scrapers.spiders.det_great_lakes_water_authority import DetGreatLakesWaterAuthoritySpider

with open('tests/files/det_great_lakes_water_authority.json', 'r') as f:
    test_response = json.load(f)

spider = DetGreatLakesWaterAuthoritySpider()
parsed_items = [item for item in spider._parse_events([(item, None) for item in test_response])]


def test_name():
    assert parsed_items[0]['name'] == 'Audit Committee'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2019, 12, 20), 'time': time(8, 0), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {'date': date(2019, 12, 20), 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'det_great_lakes_water_authority/201912200800/x/audit_committee'


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Water Board Building',
        'address': '735 Randolph St Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://glwater.legistar.com/Calendar.aspx',
        'note': ''
    }]


def test_classification():
    assert parsed_items[0]['classification'] == 'Committee'


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
