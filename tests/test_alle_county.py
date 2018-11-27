import datetime
import json
import os

import pytest
from freezegun import freeze_time

from city_scrapers.spiders.alle_county import AlleCountySpider

freezer = freeze_time('2018-11-27')
freezer.start()
spider = AlleCountySpider()
with open(os.path.join(os.path.dirname(__file__), 'files', 'alle_county.json'), 'r') as f:
    test_response = json.load(f)
parsed_items = [item for item in spider._parse_events(test_response)]
freezer.stop()


@pytest.mark.parametrize('item', [parsed_items[0]['name']])
def test_name(item):
    assert item == 'Committee on Economic Development & Housing'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert (
        parsed_items[0]['start'] == {
            'date': datetime.date(2018, 11, 29),
            'time': datetime.time(16, 0),
            'note': ''
        }
    )


def test_end():
    assert (
        parsed_items[0]['end'] == {
            'date': datetime.date(2018, 11, 29),
            'time': datetime.time(19, 0),
            'note': 'Estimated 3 hours after start time'
        }
    )


def test_id():
    assert (
        parsed_items[0]['id'] ==
        'alle_county/201811291600/x/committee_on_economic_development_housing'
    )


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    assert (
        parsed_items[0]['location'] == {
            'address': 'Conference Room 1, 436 Grant Street, Pittsburgh, PA 15219',
            'name': '',
            'neighborhood': ''
        }
    )


def test_sources():
    assert (
        parsed_items[0]['sources'] == [{
            'url': (
                'https://alleghenycounty.legistar.com/DepartmentDetail.aspx?'
                'ID=26123&GUID=8FFCC73B-C367-4473-973C-A3ECEAB40204'
            ),
            'note': ''
        }]
    )


def test_documents():
    assert (
        parsed_items[0]['documents'][0]['url'] == (
            'https://alleghenycounty.legistar.com/'
            'View.ashx?M=A&ID=653341&GUID=8115385F-D042-4E6C-A884-E58F5AEFF23F'
        )
    )


@pytest.mark.parametrize('item', [parsed_items[0]['all_day']])
def test_all_day(item):
    assert item is False


def test_classification():
    assert parsed_items[0]['classification'] == 'City Council'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
