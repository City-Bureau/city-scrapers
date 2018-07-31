from datetime import date, time

import pytest
# Adapted from test_chi_parks.py
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.spiders.wayne_building_authority import Wayne_building_authoritySpider


freezer = freeze_time('2018-03-27 12:00:01')
freezer.start()
test_response = file_response(
    'files/wayne_building_authority_meetings.html', url='https://www.waynecounty.com/boards/buildingauthority/meetings.aspx')
spider = Wayne_building_authoritySpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


# PARAMETRIZED TESTS

# @pytest.mark.parametrize('item', parsed_items)
# def test_event_description(item):
#     assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    expected_location = ({
        'name': '6th Floor, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    })
    assert item['location'] == expected_location


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'Wayne County Building Authority'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end'] == {
        'date': None,
        'time': None,
        'note': '',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': 'https://www.waynecounty.com/boards/buildingauthority/meetings.aspx',
        'note': ''
    }]


# NON-PARAMETRIZED TESTS
def test_documents():
    assert parsed_items[-1]['documents'] == []


def test_start():
    assert parsed_items[-1]['start'] == {
        'date': date(2018, 1, 17),
        'time': time(10, 0),
        'note': '',
    }


def test_id():
    assert parsed_items[-1]['id'] == 'wayne_building_authority/201801171000/x/wayne_county_building_authority'


def test_status():
    assert parsed_items[-1]['status'] == 'cancelled'
