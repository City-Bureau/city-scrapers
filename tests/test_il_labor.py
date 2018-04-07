# -*- coding: utf-8 -*-
import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.il_labor import Il_laborSpider


test_response = file_response('files/il_labor.html', url='https://www.illinois.gov/ilrb/meetings/Pages/default.aspx')
spider = Il_laborSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Local panel meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    EXPECTED_DESCRIPTION = ("The Illinois Public Labor Relations Act (Act) governs labor relations "
                "between most public employers in Illinois and their employees. Throughout "
                "the State, the Illinois Labor Relations Board regulates the designation of "
                "employee representatives; the negotiation of wages, hours, and other conditions "
                "of employment; and resolves, or if necessary, adjudicates labor disputes.")
    assert item['description'] == EXPECTED_DESCRIPTION


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_start_time():
    assert parsed_items[1]['start_time'].isoformat() == '2017-09-12T13:00:00-05:00'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None


def test_id():
    assert parsed_items[1]['id'] == 'il_labor/201709121300/x/state_panel_meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'committee-meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': None,
        'address': '160 N. LaSalle Street, Room N-401, Chicago, IL',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }

    assert parsed_items[1]['location'] == {
        'url': None,
        'address': 'Conference Room 5A, 801 S. 7th Street, Springfield, IL',
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.illinois.gov/ilrb/meetings/Pages/default.aspx', 'note': ''}]
