# -*- coding: utf-8 -*-

import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.regionaltransit import RegionaltransitSpider

events_response = file_response('files/rta_calendar.html', url='http://www.rtachicago.org/about-us/board-meetings')
events_response.meta['description'] = "Test Description"
spider = RegionaltransitSpider()
parsed_items = [item for item in spider.parse_iframe(events_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors'


def test_description():
    assert parsed_items[0]['description'] == 'Test Description'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-08-24T08:30:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'regionaltransit/201708240830/x/board_of_directors'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': 'http://www.rtachicago.org/index.php/about-us/contact-us.html',
        'name': 'RTA Administrative Offices',
        'coordinates': {'longitude': '', 'latitude': ''},
        'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604'
    }


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://www.rtachicago.org/about-us/board-meetings',
                                'note': ''}]
